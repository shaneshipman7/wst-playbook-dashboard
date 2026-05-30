import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def scrape_wst_playbooks():
    print("🔍 Scraping Wild Swing Trades blog...")
    base_url = "https://wildswingtrades.blogspot.com"
    response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    playbooks = []
    
    # Find all post links on main page
    for h3 in soup.find_all("h3"):
        a = h3.find("a")
        if not a:
            continue
        title = a.text.strip()
        link = a["href"]
        if not link.startswith("http"):
            link = base_url + link

        # Skip non-playbook posts
        if len(title) > 8 and "Swing" not in title and not re.match(r"^[A-Z]{2,5}$", title):
            continue

        # Fetch full post
        post_resp = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        post_soup = BeautifulSoup(post_resp.text, "html.parser")
        
        # Find the table inside the post body
        table = post_soup.find("table")
        if not table:
            continue

        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        headers = [th.text.strip() for th in rows[0].find_all(["th", "td"])]
        
        for row in rows[1:]:
            cells = [td.text.strip() for td in row.find_all("td")]
            if len(cells) < 5:
                continue

            # Map table columns to our standard format
            scenario = cells[0] if len(cells) > 0 else ""
            entry = cells[1] if len(cells) > 1 else ""
            stop = cells[2] if len(cells) > 2 else ""
            targets = cells[3] if len(cells) > 3 else ""
            rr = cells[4] if len(cells) > 4 else ""
            prob = cells[5] if len(cells) > 5 else ""

            playbooks.append({
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Ticker": title,
                "Post_Title": title,
                "Scenario": scenario,
                "Entry": entry,
                "Stop_Loss": stop,
                "Targets": targets,
                "R_R_Ratio": rr,
                "Est_Probability": prob,
                "Link": link
            })

    df = pd.DataFrame(playbooks)
    df.to_csv("playbooks.csv", index=False)
    print(f"✅ Saved {len(df)} plays to playbooks.csv")
    return df

if __name__ == "__main__":
    scrape_wst_playbooks()
