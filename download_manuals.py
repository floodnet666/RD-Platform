import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

def main():
    url = "https://oko-lab.com/downloads/"
    download_dir = "D:\\OKOlab\\manuals"
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        
    print(f"Buscando manuais em {url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar a página: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all links that end with .pdf
    pdf_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.pdf'):
            full_url = urllib.parse.urljoin(url, href)
            pdf_links.append(full_url)
            
    # Some sites use different elements or redirects for downloads, let's also check if there are buttons
    # if pdf_links is empty, we might need a different approach
    pdf_links = list(set(pdf_links))
    print(f"Encontrados {len(pdf_links)} links para PDF.")
    
    # Baixando os 3 primeiros para teste (ou todos)
    for pdf_url in pdf_links:
        filename = pdf_url.split("/")[-1]
        filepath = os.path.join(download_dir, filename)
        
        if os.path.exists(filepath):
            print(f"O arquivo {filename} já existe, pulando...")
            continue
            
        print(f"Baixando {filename}...")
        try:
            pdf_res = requests.get(pdf_url, headers=headers, stream=True)
            pdf_res.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in pdf_res.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            print(f"Erro ao baixar {pdf_url}: {e}")

if __name__ == "__main__":
    main()
