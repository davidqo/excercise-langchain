import os
import sys
import json
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

print("\n=== [DEBUG] ЗАПУСК УТИЛИТЫ ИНДЕКСАЦИИ ===")
print(f"[LOG] Текущая рабочая папка терминала (CWD): {os.getcwd()}")
print(f"[LOG] Папка, где лежит сам скрипт index_cli.py: {SCRIPT_DIR}")
print(f"[LOG] Абсолютный путь к искомому config.json: {CONFIG_PATH}")

def main():
    # 2. Проверяем конфиг
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ [ERROR] Файл конфигурации не найден по пути: {CONFIG_PATH}")
        sys.exit(1)
        
    print("[LOG] Файл config.json успешно найден. Читаю содержимое...")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    # 3. Вычисляем корень проекта (выходим из src/rag на два уровня вверх)
    ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
    print(f"[LOG] Вычисленный корень всего проекта (ROOT_DIR): {ROOT_DIR}")
    
    # Склеиваем пути из конфига с корнем проекта
    raw_docs_dir = cfg["indexer"]["docs_dir"]
    raw_persist_dir = cfg["chroma"]["persist_directory"]
    raw_embedding_cache_dir = cfg["embeddings"].get("cache_dir", "./.cache/huggingface")
    
    docs_dir = os.path.abspath(os.path.join(ROOT_DIR, raw_docs_dir))
    persist_dir = os.path.abspath(os.path.join(ROOT_DIR, raw_persist_dir))
    embedding_cache_dir = os.path.abspath(os.path.join(ROOT_DIR, raw_embedding_cache_dir))
    
    print(f"[LOG] Путь к документам из конфига: '{raw_docs_dir}'")
    print(f"[LOG] Итоговый абсолютный путь к документам на ПК: {docs_dir}")
    print(f"[LOG] Итоговый абсолютный путь к базе ChromaDB на ПК: {persist_dir}")
    print(f"[LOG] Итоговый абсолютный путь к кешу модели эмбеддингов: {embedding_cache_dir}")
    
    # 4. Проверяем физическое существование папки с доками
    if not os.path.exists(docs_dir):
        print(f"❌ [ERROR] Директория с документами НЕ СУЩЕСТВУЕТ на диске: {docs_dir}")
        sys.exit(1)
        
    # 5. Смотрим, что вообще лежит в этой папке
    all_files_in_dir = os.listdir(docs_dir)
    print(f"[LOG] Список ВСЕХ файлов, обнаруженных в папке документов: {all_files_in_dir}")
    
    files = [f for f in all_files_in_dir if f.endswith('.txt')]
    print(f"[LOG] Найдено файлов с расширением .txt: {len(files)} -> {files}")

    if not files:
        print(f"❌ [ERROR] Нечего индексировать. В папке {docs_dir} нет .txt файлов.")
        sys.exit(0)

    # 6. Если файлы есть, пошла стандартная логика
    print("\n🚀 Локальная индексация напрямую в файлы SQLite...")
    os.makedirs(embedding_cache_dir, exist_ok=True)
    if os.listdir(embedding_cache_dir):
        print("-> Инициализация модели эмбеддингов из локального кеша...")
    else:
        print("-> Локальный кеш модели пуст. При первом запуске модель будет скачана...")
    embeddings = HuggingFaceEmbeddings(
        model_name=cfg["embeddings"]["model_name"],
        cache_folder=embedding_cache_dir,
    )
    
    vector_store = Chroma(
        collection_name=cfg["chroma"]["collection_name"],
        embedding_function=embeddings,
        persist_directory=persist_dir
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg["indexer"]["chunk_size"], 
        chunk_overlap=cfg["indexer"]["chunk_overlap"]
    )

    for file_name in files:
        file_path = os.path.join(docs_dir, file_name)
        print(f"   [Обработка] Читаю файл: {file_path}")
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            chunks = text_splitter.split_documents(loader.load())
            
            vector_store.add_documents(chunks)
            print(f"   [Успешно] Файл {file_name} обработан. Добавлено чанков: {len(chunks)}")
        except Exception as e:
            print(f"   ❌ [ERROR] Ошибка при обработке {file_name}: {e}")

    print("=== ✅ ИНДЕКСАЦИЯ ПОЛНОСТЬЮ ЗАВЕРШЕНА ===")

if __name__ == "__main__":
    main()
