import sys
from pathlib import Path
from unittest.mock import MagicMock

# Stub torch for tests
sys.modules.setdefault("torch", MagicMock())

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from app.db.models import Book, Chapter, Chunk, WordTimestamp
from app.services import jobs as job_svc
from app.services.tts.indic_parler import HINDI_PRESETS, DEFAULT_DESCRIPTION
from app.services.tts.router import synthesize


@pytest.fixture
def test_db_env(tmp_path, monkeypatch):
    """Isolated SQLite DB for voice tests."""
    db_path = tmp_path / "voice_test.sqlite"
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()

    monkeypatch.setattr("app.config.DB_PATH", db_path)
    monkeypatch.setattr("app.config.AUDIO_DIR", audio_dir)
    monkeypatch.setattr("app.services.jobs.config.AUDIO_DIR", audio_dir)

    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr("app.db.database.engine", test_engine)
    monkeypatch.setattr("app.services.jobs.engine", test_engine)

    SQLModel.metadata.create_all(test_engine)
    return test_engine


def test_import_parsed_book_stores_voice(test_db_env):
    """Verify that importing a book with custom voice options sets the database fields."""
    engine = test_db_env

    class DummyChapter:
        def __init__(self, title, text):
            self.title = title
            self.text = text

    class DummyParsedBook:
        def __init__(self):
            self.title = "Voice Book"
            self.author = "Author"
            self.cover_bytes = None
            self.chapters = [DummyChapter("Ch 1", "Hello world")]

    dummy_source = Path(engine.url.database).parent / "voice_dummy.txt"
    dummy_source.write_text("dummy")

    parsed = DummyParsedBook()
    book_id = job_svc.import_parsed_book(
        parsed,
        source_path=dummy_source,
        language_override="en",
        voice_id="af_sarah",
        voice_prompt="some_preset_id",
    )

    with Session(engine) as session:
        book = session.get(Book, book_id)
        assert book is not None
        assert book.voice_id == "af_sarah"
        assert book.voice_prompt == "some_preset_id"


def test_voice_change_resets_narration(test_db_env, monkeypatch):
    """Updating a book's voice should wipe out existing audio outputs and reset chapters/chunks to pending."""
    engine = test_db_env
    audio_dir = Path(engine.url.database).parent / "audio"

    # Seed DB with a book, chapter, chunk, and word timestamp
    with Session(engine) as session:
        book = Book(
            title="Update Test",
            source_file_path="/tmp/dummy.txt",
            language="en",
            voice_id="af_heart",
        )
        session.add(book)
        session.commit()
        session.refresh(book)
        book_id = book.id

        chapter = Chapter(
            book_id=book_id,
            index=0,
            title="Ch 1",
            status="ready",
            audio_path=str(audio_dir / f"book{book_id}" / "chapter_0.wav"),
            start_ms=0,
            duration_ms=1000,
        )
        session.add(chapter)
        session.commit()
        session.refresh(chapter)

        wt = WordTimestamp(
            chapter_id=chapter.id,
            word="hello",
            start_ms=0,
            end_ms=500,
            char_start=0,
            char_end=5,
        )
        session.add(wt)

        chunk = Chunk(
            chapter_id=chapter.id,
            index=0,
            text="hello",
            status="ready",
            audio_path=str(audio_dir / f"book{book_id}" / "ch1" / "chunk0.wav"),
        )
        session.add(chunk)
        session.commit()

    # Create dummy files
    ch_audio = audio_dir / f"book{book_id}" / "chapter_0.wav"
    ch_audio.parent.mkdir(parents=True, exist_ok=True)
    ch_audio.write_bytes(b"ch_wav")

    chunk_audio = audio_dir / f"book{book_id}" / "ch1" / "chunk0.wav"
    chunk_audio.parent.mkdir(parents=True, exist_ok=True)
    chunk_audio.write_bytes(b"chunk_wav")

    # Perform PATCH-like operation
    from fastapi import HTTPException
    from app.main import update_book

    # Call update_book with different voice_id
    monkeypatch.setattr("app.main.get_session", lambda: Session(engine))
    update_book(book_id, voice_id="af_sarah")

    with Session(engine) as session:
        # Check database reset
        updated_book = session.get(Book, book_id)
        assert updated_book.voice_id == "af_sarah"
        assert updated_book.total_duration_ms == 0

        updated_chapter = session.exec(select(Chapter).where(Chapter.book_id == book_id)).first()
        assert updated_chapter.status == "pending"
        assert updated_chapter.audio_path is None
        assert updated_chapter.start_ms == 0
        assert updated_chapter.duration_ms == 0

        updated_chunk = session.exec(select(Chunk).where(Chunk.chapter_id == updated_chapter.id)).first()
        assert updated_chunk.status == "pending"
        assert updated_chunk.audio_path is None

        # Verify word timestamps deleted
        wts = session.exec(select(WordTimestamp).where(WordTimestamp.chapter_id == updated_chapter.id)).all()
        assert len(wts) == 0

    # Check files deleted
    assert not ch_audio.exists()
    assert not chunk_audio.exists()


def test_hindi_presets_resolution(monkeypatch):
    """Check that the Hindi presets resolve correctly in synthesize_hindi."""
    synth_mock = MagicMock()
    monkeypatch.setattr("app.services.tts.indic_parler._load", lambda: (MagicMock(config=MagicMock(sampling_rate=24000)), MagicMock(), MagicMock()))
    
    # Check resolution
    from app.services.tts.indic_parler import synthesize_hindi
    
    # Mock model generate and soundfile write
    monkeypatch.setattr("torch.no_grad", MagicMock())
    monkeypatch.setattr("soundfile.write", MagicMock())
    
    desc_tokenizer_mock = MagicMock()
    model_mock = MagicMock()
    model_mock.config = MagicMock(sampling_rate=24000, text_encoder=MagicMock(_name_or_path="test"))
    
    import numpy as np
    gen_output_mock = MagicMock()
    gen_output_mock.cpu().numpy().squeeze.return_value = np.array([0.1, 0.2], dtype=np.float32)
    model_mock.generate.return_value = gen_output_mock

    monkeypatch.setattr("app.services.tts.indic_parler._load", lambda: (
        model_mock, 
        MagicMock(), 
        desc_tokenizer_mock
    ))
    
    # Call synthesize_hindi
    synthesize_hindi("नमस्ते", Path("/tmp/dummy.wav"), voice_prompt="deep_expressive_male")
    
    # Assert that tokenizer was called with the deep_expressive_male description prompt
    desc_tokenizer_mock.assert_called_once_with(HINDI_PRESETS["deep_expressive_male"], return_tensors="pt")


def test_import_local_file_endpoint(test_db_env, monkeypatch):
    """Verify that the /import-path endpoint copy-imports a local file and stores metadata."""
    engine = test_db_env
    db_dir = Path(engine.url.database).parent
    
    # Create a dummy source file
    src_file = db_dir / "my_source_book.txt"
    src_file.write_text("Chapter 1\nSome local book content.")

    from fastapi.testclient import TestClient
    from app.main import app

    # Mock get_session dependency and parse_document
    monkeypatch.setattr("app.main.get_session", lambda: Session(engine))
    monkeypatch.setattr("app.main.job_svc.import_parsed_book", lambda parsed, dest, override, voice_id, voice_prompt: 1)
    
    class DummyParsedBook:
        title = "Mock Book Title"
        author = None
        chapters = []
        cover_bytes = None
    
    monkeypatch.setattr("app.main.parse_document", lambda dest: DummyParsedBook())

    client = TestClient(app)
    
    # Call the endpoint
    res = client.post(
        "/import-path",
        data={
            "path": str(src_file),
            "language": "hi",
            "voice_prompt": "deep_expressive_male"
        }
    )
    
    assert res.status_code == 200
    data = res.json()
    assert data["book_id"] == 1
    assert data["title"] == "Mock Book Title"


def test_rename_delete_book(test_db_env, monkeypatch):
    """Verify that PATCH updates the title and DELETE cleans up the database rows."""
    engine = test_db_env
    
    from fastapi.testclient import TestClient
    from app.main import app
    
    monkeypatch.setattr("app.main.get_session", lambda: Session(engine))
    client = TestClient(app)
    
    # 1. Seed a book
    with Session(engine) as session:
        book = Book(
            title="Old Title",
            source_file_path="/tmp/old.txt",
            language="en"
        )
        session.add(book)
        session.commit()
        session.refresh(book)
        book_id = book.id

    # 2. PATCH to rename
    patch_res = client.patch(
        f"/books/{book_id}",
        params={"title": "New Title"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "New Title"
    
    # 3. DELETE to remove
    del_res = client.delete(f"/books/{book_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"status": "deleted"}
    
    # 4. Verify book is gone from database
    with Session(engine) as session:
        deleted_book = session.get(Book, book_id)
        assert deleted_book is None

