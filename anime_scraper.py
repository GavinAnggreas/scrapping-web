import requests
from bs4 import BeautifulSoup
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

def scrape_anime_data(search_query=None, limit=100):
    try:
        base_url = "https://s7.nontonanimeid.boats"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        anime_list = []
        page = 1
        anime_per_page = 20
        
        print(f"🎯 Scraping anime with target limit: {limit}")
        
        while len(anime_list) < limit:
            if search_query:
                url = f"{base_url}/?s={search_query}"
                if page > 1:
                    url = f"{base_url}/page/{page}/?s={search_query}"
            else:
                url = base_url if page == 1 else f"{base_url}/page/{page}/"
            
            print(f"📄 Scraping page {page}: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
            
                main_content = soup.find('main', class_='content')
                if main_content:
                    postbaru_section = main_content.find('section', id='postbaru')
                    if postbaru_section:
                        misha_posts_wrap = postbaru_section.find('div', class_='misha_posts_wrap')
                        if misha_posts_wrap:
                             Find all anime articles with correct class pattern
                            anime_articles = misha_posts_wrap.find_all('article', class_=re.compile(r'animeseries post-\d+'))
                            print(f"   Found {len(anime_articles)} anime articles on page {page}")
                            
                            if len(anime_articles) == 0:
                                print(f"   No more anime found on page {page}, stopping...")
                                break
                            
                            for article in anime_articles:
                                if len(anime_list) >= limit:
                                    break
                                
                                try:
                                    sera_div = article.find('div', class_='sera')
                                    if not sera_div:
                                        continue

                                    title = None
                                    
                                    title_element = article.find('h2', class_='entry-title') or article.find('h3', class_='entry-title')
                                    if title_element:
                                        title = title_element.get_text(strip=True)
                                    
                                    if not title:
                                        title_elem = article.find('a', class_='entry-title')
                                        if title_elem:
                                            title = title_elem.get('title') or title_elem.get_text(strip=True)
                                    if not title:
                                        title_elem = article.find('a', title=True)
                                        if title_elem:
                                            title = title_elem.get('title')
                                    
                                     Method 4: Look for any text that might be title
                                    if not title:
                                         Find the first meaningful text in the article
                                        for elem in article.find_all(['h2', 'h3', 'h4', 'a']):
                                            if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 3:
                                                title = elem.get_text(strip=True)
                                                break
                                    
                                    if not title:
                                        continue
                                    
                                    anime_link = None
                                    link_elem = sera_div.find('a', href=True) if sera_div else None
                                    if not link_elem:
                                        link_elem = article.find('a', href=True)
                                    
                                    if link_elem:
                                        anime_link = link_elem['href']
                                    
                                    image_url = None
                                    if sera_div:
                                        img_elem = sera_div.find('img')
                                        if img_elem and img_elem.get('src'):
                                            image_url = img_elem['src']
                                        else:
                                            style = sera_div.get('style', '')
                                            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)', style)
                                            if bg_match:
                                                image_url = bg_match.group(1)
                                    
                                    if not image_url:
                                        img_elem = article.find('img')
                                        if img_elem and img_elem.get('src'):
                                            image_url = img_elem['src']
                                    
                                    if not image_url:
                                        image_url = "https://via.placeholder.com/150x200/4A90E2/FFFFFF?text=Anime"
                                    
                                    rating_elem = article.find('span', class_='value')
                                    if not rating_elem:
                                        rating_elem = article.find('span', class_='rating')
                                    rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
                                    
                                    type_elem = article.find('span', class_='type')
                                    anime_type = type_elem.get_text(strip=True) if type_elem else "TV"
                                    
                                    anime_data = {
                                        'title': title,
                                        'image_url': image_url,
                                        'link': anime_link,
                                        'rating': rating,
                                        'type': anime_type
                                    }
                                    
                                    anime_list.append(anime_data)
                                    
                                except Exception as e:
                                    print(f"   Error processing anime article: {e}")
                                    continue
                        else:
                            print(f"   Could not find div.misha_posts_wrap on page {page}")
                            break
                    else:
                        print(f"   Could not find section#postbaru on page {page}")
                        break
                else:
                    print(f"   Could not find main.content on page {page}")
                    break
                
                if len(anime_articles) < anime_per_page:
                    print(f"   Page {page} has fewer anime than expected, stopping...")
                    break
                
                page += 1
                
                if page > 100: 
                    print(f"   Reached maximum page limit (100), stopping...")
                    break
                
            except Exception as e:
                print(f"   Error scraping page {page}: {e}")
                break
        
        print(f"🎉 Successfully scraped {len(anime_list)} anime from {page-1} pages")
        return anime_list
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def get_anime_details(anime_url):
    """Get detailed information about a specific anime"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(anime_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_elem = soup.find('h1', class_='entry-title')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        img_elem = soup.find('div', class_='anime-card_sidebar').find('img') if soup.find('div', class_='anime-card_sidebar') else None
        if not img_elem:
            img_elem = soup.find('img', class_='attachment-post-thumbnail')
        
        image_url = img_elem['src'] if img_elem and img_elem.get('src') else None

        synopsis_elem = soup.find('div', class_='entry-content') or soup.find('div', class_='sinopsis')
        synopsis = synopsis_elem.get_text(strip=True) if synopsis_elem else "No synopsis available"
        
        rating_elem = soup.find('span', class_='value')
        if not rating_elem:
            rating_elem = soup.find('span', class_='rating')
        rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
        
        type_elem = soup.find('span', class_='type')
        anime_type = type_elem.get_text(strip=True) if type_elem else "TV"
        
        details_list = soup.find('ul', class_='details-list')
        details = {}
        if details_list:
            detail_items = details_list.find_all('li')
            for item in detail_items:
                text = item.get_text(strip=True)
                if ':' in text:
                    key, value = text.split(':', 1)
                    details[key.strip()] = value.strip()
        
        episodes = []
        episode_list = soup.find('div', class_='episode-list-items')
        if episode_list:
            episode_links = episode_list.find_all('a', class_='episode-item')
            for episode_link in episode_links:
                episode_url = episode_link.get('href')
                episode_text = episode_link.get_text(strip=True)
                episodes.append({
                    'text': episode_text,
                    'url': episode_url
                })
        
        return {
            'title': title,
            'image_url': image_url,
            'synopsis': synopsis,
            'rating': rating,
            'type': anime_type,
            'details': details,
            'episodes': episodes,
            'url': anime_url
        }
        
    except Exception as e:
        print(f"Error getting anime details: {e}")
        return None

@app.route('/api/search', methods=['GET'])
def search_anime():
    """API endpoint to search for anime"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    
    if not query:
        anime_list = scrape_anime_data(limit=limit)
    else:
        anime_list = scrape_anime_data(query, limit=limit)
    
    return jsonify({
        'success': True,
        'data': anime_list,
        'count': len(anime_list)
    })

@app.route('/api/anime/<path:anime_url>', methods=['GET'])
def get_anime(anime_url):
    """API endpoint to get specific anime details"""
    import urllib.parse
    decoded_url = urllib.parse.unquote(anime_url)
    
    anime_details = get_anime_details(decoded_url)
    
    if anime_details:
        return jsonify({
            'success': True,
            'data': anime_details
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch anime details'
        }), 404

@app.route('/')
def index():
    """Serve the main HTML page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Anime Search</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: 181A20;
                min-height: 100vh;
                color: f1f1f1;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                color: fff;
            }
            .header h1 {
                font-size: 2.2rem;
                margin-bottom: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                letter-spacing: 1px;
            }
            .search-container {
                background: 23242b;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
            }
            .search-box {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            .search-input {
                flex: 1;
                padding: 15px;
                border: 2px solid 23242b;
                border-radius: 10px;
                font-size: 16px;
                background: 23242b;
                color: f1f1f1;
                transition: border-color 0.3s ease;
            }
            .search-input:focus {
                outline: none;
                border-color: 764ba2;
            }
            .search-btn {
                padding: 15px 30px;
                background: linear-gradient(135deg, 764ba2 0%, 23242b 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            .search-btn:hover {
                transform: translateY(-2px);
                background: linear-gradient(135deg, 23242b 0%, 764ba2 100%);
            }
            .search-btn:active {
                transform: translateY(0);
            }
            .results-container {
                background: 23242b;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                min-height: 200px;
            }
            .anime-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .anime-card {
                background: 23242b;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
            }
            .anime-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            }
            .anime-image {
                width: 100%;
                height: 250px;
                object-fit: cover;
                background: 181A20;
            }
            .anime-info {
                padding: 15px;
            }
            .anime-title {
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
                color: f1f1f1;
                line-height: 1.3;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            .anime-rating {
                font-size: 12px;
                color: ffd700;
                background: 23242b;
                padding: 4px 8px;
                border-radius: 15px;
                display: inline-block;
                margin-right: 8px;
                border: 1px solid 333;
            }
            .anime-type {
                font-size: 11px;
                color: aaa;
                background: 181A20;
                padding: 3px 6px;
                border-radius: 10px;
                display: inline-block;
                border: 1px solid 23242b;
            }
            .loading, .no-results {
                text-align: center;
                padding: 40px;
                color: aaa;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.85);
                backdrop-filter: blur(5px);
            }
            .modal-content {
                background-color: 23242b;
                margin: 5% auto;
                padding: 30px;
                border-radius: 15px;
                width: 90%;
                max-width: 600px;
                max-height: 80vh;
                overflow-y: auto;
                position: relative;
                color: f1f1f1;
            }
            .close {
                color: aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                position: absolute;
                right: 20px;
                top: 15px;
            }
            .close:hover {
                color: fff;
            }
            .modal-image {
                width: 100%;
                max-height: 400px;
                object-fit: cover;
                border-radius: 10px;
                margin-bottom: 20px;
                background: 181A20;
            }
            .modal-title {
                font-size: 1.5rem;
                margin-bottom: 15px;
                color: fff;
            }
            .modal-synopsis {
                color: ccc;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .modal-rating {
                background: 181A20;
                padding: 10px 15px;
                border-radius: 10px;
                color: ffd700;
                display: inline-block;
                margin-bottom: 15px;
            }
            .modal-details {
                background: 181A20;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
            }
            .modal-details h3 {
                margin-bottom: 10px;
                color: fff;
                font-size: 1.1rem;
            }
            .modal-details ul {
                list-style: none;
                padding: 0;
            }
            .modal-details li {
                padding: 5px 0;
                border-bottom: 1px solid 23242b;
            }
            .modal-details li:last-child {
                border-bottom: none;
            }
            .modal-episodes {
                margin-top: 20px;
            }
            .modal-episodes h3 {
                margin-bottom: 15px;
                color: fff;
                font-size: 1.1rem;
            }
            .episodes-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
                max-height: 300px;
                overflow-y: auto;
            }
            .episode-item {
                background: 23242b;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: background-color 0.2s ease;
                border: 1px solid 181A20;
            }
            .episode-item:hover {
                background: 181A20;
            }
            .episode-item a {
                color: f1f1f1;
                text-decoration: none;
                display: block;
            }
            selectanimeLimit {
                padding: 5px;
                border: 1px solid 23242b;
                border-radius: 5px;
                background: 181A20;
                color: f1f1f1;
            }
            @media (max-width: 768px) {
                .container {
                    padding: 15px;
                }
                .header h1 {
                    font-size: 2rem;
                }
                .search-box {
                    flex-direction: column;
                }
                .anime-grid {
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 15px;
                }
                .modal-content {
                    width: 95%;
                    margin: 10% auto;
                    padding: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Anime Search</h1>
            </div>
            <div class="search-container">
                <div class="search-box">
                    <input type="text" class="search-input" id="searchInput" placeholder="Masukkan judul anime yang ingin dicari...">
                    <button class="search-btn" onclick="searchAnime()">🔍 Cari</button>
                </div>
                <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 15px;">
                    <label for="animeLimit" style="color: aaa; font-size: 14px; margin-right: 8px;">Jumlah Anime:</label>
                    <select id="animeLimit">
                        <option value="50">50</option>
                        <option value="100" selected>100</option>
                        <option value="200">200</option>
                        <option value="500">500</option>
                        <option value="1000">1000</option>
                        <option value="2000">2000</option>
                    </select>
                </div>
            </div>
            <div class="results-container">
                <div id="resultsContent">
                    <div class="loading">
                        <p>Memuat anime terbaru...</p>
                    </div>
                </div>
            </div>
        </div>
        <!-- Modal for anime details -->
        <div id="animeModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <img id="modalImage" class="modal-image" src="" alt="">
                <h2 id="modalTitle" class="modal-title"></h2>
                <div id="modalRating" class="modal-rating"></div>
                <div id="modalDetails" class="modal-details"></div>
                <p id="modalSynopsis" class="modal-synopsis"></p>
                <div id="modalEpisodes" class="modal-episodes"></div>
            </div>
        </div>
        <script>
            let currentAnimeList = [];
            window.onload = function() {
                loadLatestAnime();
            };
            function searchAnime() {
                const query = document.getElementById('searchInput').value.trim();
                if (query === '') {
                    loadLatestAnime();
                } else {
                    performSearch(query);
                }
            }
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchAnime();
                }
            });
            document.getElementById('animeLimit').addEventListener('change', function() {
                if (document.getElementById('searchInput').value.trim() === '') {
                    loadLatestAnime();
                }
            });
            async function loadLatestAnime() {
                try {
                    const limit = document.getElementById('animeLimit').value;
                    showLoading(`Memuat ${limit} anime terbaru...<br><small>Ini akan memakan waktu beberapa saat karena mengambil dari banyak halaman</small>`);
                    const response = await fetch(`/api/search?limit=${limit}`);
                    const data = await response.json();
                    if (data.success) {
                        currentAnimeList = data.data;
                        displayResults(data.data, `${limit} Anime Terbaru`);
                    } else {
                        showError('Gagal memuat anime terbaru');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showError('Terjadi kesalahan saat memuat data');
                }
            }
            async function performSearch(query) {
                try {
                    const limit = document.getElementById('animeLimit').value;
                    showLoading(`Mencari "${query}" (maksimal ${limit} hasil)...`);
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=${limit}`);
                    const data = await response.json();
                    if (data.success) {
                        currentAnimeList = data.data;
                        displayResults(data.data, `Hasil pencarian untuk "${query}" (${data.count} anime)`);
                    } else {
                        showError('Gagal melakukan pencarian');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showError('Terjadi kesalahan saat mencari');
                }
            }
            function displayResults(animeList, title) {
                const resultsContent = document.getElementById('resultsContent');
                if (animeList.length === 0) {
                    resultsContent.innerHTML = `
                        <div class="no-results">
                            <p>Tidak ada anime yang ditemukan</p>
                            <p>Coba kata kunci yang berbeda</p>
                        </div>
                    `;
                    return;
                }
                const resultsHTML = `
                    <h2 style="margin-bottom: 20px; color: fff; text-align: center;">${title}</h2>
                    <div class="anime-grid">
                        ${animeList.map(anime => `
                            <div class="anime-card" onclick="showAnimeDetails('${anime.link || ''}', '${anime.title}')">
                                <img src="${anime.image_url}" alt="${anime.title}" class="anime-image" 
                                     onerror="this.src='https://via.placeholder.com/200x250/4A90E2/FFFFFF?text=Anime'">
                                <div class="anime-info">
                                    <div class="anime-title">${anime.title}</div>
                                    <div style="display: flex; align-items: center; margin-top: 8px;">
                                        <div class="anime-rating">★ ${anime.rating}</div>
                                        <div class="anime-type">${anime.type || 'TV'}</div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                resultsContent.innerHTML = resultsHTML;
            }
            function showLoading(message) {
                document.getElementById('resultsContent').innerHTML = `
                    <div class="loading">
                        <p>${message}</p>
                    </div>
                `;
            }
            function showError(message) {
                document.getElementById('resultsContent').innerHTML = `
                    <div class="no-results">
                        <p style="color: e74c3c;">${message}</p>
                    </div>
                `;
            }
            async function showAnimeDetails(animeUrl, animeTitle) {
                if (!animeUrl) {
                    alert('Link anime tidak tersedia');
                    return;
                }
                try {
                    const response = await fetch(`/api/anime/${encodeURIComponent(animeUrl)}`);
                    const data = await response.json();
                    if (data.success) {
                        const anime = data.data;
                        document.getElementById('modalImage').src = anime.image_url || 'https://via.placeholder.com/400x300/4A90E2/FFFFFF?text=No+Image';
                        document.getElementById('modalTitle').textContent = anime.title;
                        document.getElementById('modalRating').textContent = `★ Rating: ${anime.rating} | Type: ${anime.type || 'TV'}`;
                        const detailsDiv = document.getElementById('modalDetails');
                        if (anime.details && Object.keys(anime.details).length > 0) {
                            let detailsHTML = '<h3>Details:</h3><ul>';
                            for (const [key, value] of Object.entries(anime.details)) {
                                detailsHTML += `<li><strong>${key}:</strong> ${value}</li>`;
                            }
                            detailsHTML += '</ul>';
                            detailsDiv.innerHTML = detailsHTML;
                        } else {
                            detailsDiv.innerHTML = '';
                        }
                        document.getElementById('modalSynopsis').textContent = anime.synopsis;
                        const episodesDiv = document.getElementById('modalEpisodes');
                        if (anime.episodes && anime.episodes.length > 0) {
                            let episodesHTML = '<h3>Episodes:</h3><div class="episodes-grid">';
                            anime.episodes.forEach(episode => {
                                episodesHTML += `<div class="episode-item"><a href="${episode.url}" target="_blank">${episode.text}</a></div>`;
                            });
                            episodesHTML += '</div>';
                            episodesDiv.innerHTML = episodesHTML;
                        } else {
                            episodesDiv.innerHTML = '';
                        }
                        document.getElementById('animeModal').style.display = 'block';
                    } else {
                        alert('Gagal memuat detail anime');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Terjadi kesalahan saat memuat detail anime');
                }
            }
            function closeModal() {
                document.getElementById('animeModal').style.display = 'none';
            }
            window.onclick = function(event) {
                const modal = document.getElementById('animeModal');
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting Anime Search Website...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔍 Search for anime titles or leave empty to see latest anime")
    app.run(debug=True, host='0.0.0.0', port=5000)

