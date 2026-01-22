#!/usr/bin/env python3
"""
Search Server - бесплатный поиск через DuckDuckGo
"""

import asyncio
from aiohttp import web
from duckduckgo_search import DDGS

async def search(request):
    """Поиск в интернете через DuckDuckGo"""
    try:
        data = await request.json()
        query = data.get("query", "")
        max_results = data.get("max_results", 5)
        
        if not query:
            return web.json_response({"error": "No query provided"}, status=400)
        
        print(f"🔍 Поиск: '{query}'")
        
        # Выполняем поиск
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        # Форматируем результаты
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "url": r.get("href", "")
            })
        
        print(f"✅ Найдено {len(formatted)} результатов")
        
        return web.json_response({
            "query": query,
            "results": formatted
        })
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def news(request):
    """Поиск новостей через DuckDuckGo"""
    try:
        data = await request.json()
        query = data.get("query", "")
        max_results = data.get("max_results", 5)
        
        if not query:
            return web.json_response({"error": "No query provided"}, status=400)
        
        print(f"📰 Новости: '{query}'")
        
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
        
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "url": r.get("url", ""),
                "date": r.get("date", ""),
                "source": r.get("source", "")
            })
        
        print(f"✅ Найдено {len(formatted)} новостей")
        
        return web.json_response({
            "query": query,
            "results": formatted
        })
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def health(request):
    return web.json_response({"status": "ok", "service": "Search Server"})

def create_app():
    app = web.Application()
    app.router.add_post("/search", search)
    app.router.add_post("/news", news)
    app.router.add_get("/health", health)
    app.router.add_get("/", health)
    return app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5051))
    
    print("🔍 Search Server запускается...")
    print(f"📍 Адрес: http://0.0.0.0:{port}")
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=port)
