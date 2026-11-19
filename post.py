"""毎日1件、posts.json の投稿を state.json の順番どおりに Instagram へ投稿する。
一巡したら順番をランダムに並べ直す。DRY_RUN=1 のときは投稿せず内容だけ表示する。"""
import json, os, random, time, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

HOST  = os.environ.get('GRAPH_HOST', 'graph.facebook.com')   # Instagramログイン方式なら graph.instagram.com
VER   = os.environ.get('GRAPH_VERSION', 'v23.0')
TOKEN = os.environ.get('IG_ACCESS_TOKEN', '')
IGID  = os.environ.get('IG_USER_ID', '')
REPO  = os.environ.get('GITHUB_REPOSITORY', '')               # 例: user/instagram-autopost（Actionsが自動設定）
BRANCH= os.environ.get('GITHUB_REF_NAME', 'main')
DRY   = os.environ.get('DRY_RUN') == '1'

def api(path, params=None, method='POST'):
    params = dict(params or {}, access_token=TOKEN)
    url = f'https://{HOST}/{VER}/{path}'
    data = urllib.parse.urlencode(params).encode()
    if method == 'GET':
        req = urllib.request.Request(url + '?' + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f'APIエラー {e.code}: {e.read().decode()}')

def wait_ready(cid):
    for _ in range(30):
        s = api(cid, {'fields': 'status_code'}, 'GET').get('status_code')
        if s == 'FINISHED': return
        if s == 'ERROR': raise SystemExit(f'メディア処理エラー: {cid}')
        time.sleep(5)
    raise SystemExit('メディア処理がタイムアウトしました')

def img_url(pid, f):
    return f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/images/{urllib.parse.quote(pid)}/{urllib.parse.quote(f)}'

posts = {p['id']: p for p in json.load(open('posts.json', encoding='utf-8'))}
st = json.load(open('state.json', encoding='utf-8'))
# リストの増減に追従：消えた品番は除き、新しい品番は末尾へ
st['order'] = [i for i in st['order'] if i in posts] + [i for i in posts if i not in st['order']]
if st['next'] >= len(st['order']):
    random.shuffle(st['order']); st['next'] = 0
p = posts[st['order'][st['next']]]
urls = [img_url(p['id'], f) for f in p['images']]
print(f"投稿予定: {p['id']}（{st['next']+1}/{len(st['order'])}件目, 画像{len(urls)}枚）\n{p['caption'][:120]}…")
if DRY:
    print('\n'.join(urls)); raise SystemExit(0)
if not (TOKEN and IGID): raise SystemExit('IG_ACCESS_TOKEN / IG_USER_ID が未設定です')

if len(urls) == 1:
    cid = api(f'{IGID}/media', {'image_url': urls[0], 'caption': p['caption']})['id']
else:
    kids = []
    for u in urls:
        k = api(f'{IGID}/media', {'image_url': u, 'is_carousel_item': 'true'})['id']
        wait_ready(k); kids.append(k)
    cid = api(f'{IGID}/media', {'media_type': 'CAROUSEL', 'children': ','.join(kids), 'caption': p['caption']})['id']
wait_ready(cid)
mid = api(f'{IGID}/media_publish', {'creation_id': cid})['id']
jst = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
st['history'] = (st['history'] + [{'date': jst, 'id': p['id'], 'media_id': mid}])[-60:]
st['next'] += 1
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('投稿完了:', mid)
