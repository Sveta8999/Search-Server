#!/usr/bin/env python3
"""
Search Server - бесплатный поиск через DuckDuckGo
"""

import asyncio
import aiohttp
from aiohttp import web
import urllib.parse
import re

async def fetch_ddg_results(query, max_results=5):
    """Получает результаты поиска через DuckDuckGo HTML"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
    
    # Парсим результаты
    results = []
    
    # Ищем блоки результатов
    pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">(.+?)</a>.*?<a class="result__snippet"[^>]*>(.+?)</a>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for match in matches[:max_results]:
        url_encoded = match[0]
        # Декодируем URL из DuckDuckGo redirect
        if "uddg=" in url_encoded:
            url_match = re.search(r'uddg=([^&]+)', url_encoded)
            if url_match:
                url_encoded = urllib.parse.unquote(url_match.group(1))
        
        title = re.sub(r'<[^>]+>', '', match[1]).strip()
        body = re.sub(r'<[^>]+>', '', match[2]).strip()
        
        results.append({
            "title": title,
            "body": body,
            "url": url_encoded
        })
    
    return results

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
        results = await fetch_ddg_results(query, max_results)
        
        print(f"✅ Найдено {len(results)} результатов")
        
        return web.json_response({
            "query": query,
            "results": results
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
        
        # Добавляем "news" к запросу
        results = await fetch_ddg_results(f"{query} news", max_results)
        
        print(f"✅ Найдено {len(results)} новостей")
        
        return web.json_response({
            "query": query,
            "results": results
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
