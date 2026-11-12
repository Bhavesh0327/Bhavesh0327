import datetime, json, os, sys, urllib.request

OUT = sys.argv[1]
STATIC = len(sys.argv) > 2  # render final frame only, for previewing without SMIL
os.makedirs(OUT, exist_ok=True)

BG, BORDER, BAR = "#0d1117", "#30363d", "#161b22"
GREEN, DIM, MUTED, INK, BLUE, AMBER = "#39d353", "#238636", "#8b949e", "#e6edf3", "#58a6ff", "#d29922"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
CW = 8.43  # advance of a 14px monospace glyph


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def window(w, h, title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">
<defs><clipPath id="win"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{w}" height="{h}" fill="{BG}"/>
<rect width="{w}" height="38" fill="{BAR}"/>
<line x1="0" y1="38" x2="{w}" y2="38" stroke="{BORDER}"/>
<circle cx="22" cy="19" r="6" fill="#ff5f57"/><circle cx="42" cy="19" r="6" fill="#febc2e"/><circle cx="62" cy="19" r="6" fill="#28c840"/>
<text x="{w / 2}" y="24" text-anchor="middle" font-size="12" fill="{MUTED}">{title}</text>
{body}
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{BORDER}"/>
</svg>'''


def appear(at):
    return "" if STATIC else f' opacity="0"><set attributeName="opacity" to="1" begin="{at:.2f}s" fill="freeze"/'


def prompt(x, y, cmd, at, uid):
    """Prompt appears at `at`, then `cmd` types out. Returns (svg, time typing ends)."""
    p = f'<tspan fill="{GREEN}">bhavesh@github</tspan><tspan fill="{INK}">:</tspan><tspan fill="{BLUE}">~</tspan><tspan fill="{INK}">$ </tspan>'
    px = x + len("bhavesh@github:~$ ") * CW
    dur = max(0.4, len(cmd) * 0.055)
    w = len(cmd) * (CW + 1) + 24
    if STATIC:
        clip = f'<rect x="{px}" y="{y - 16}" width="{w}" height="22"/>'
    else:
        clip = f'<rect x="{px}" y="{y - 16}" width="0" height="22"><animate attributeName="width" from="0" to="{w}" begin="{at + 0.35:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect>'
    s = f'''<g{appear(at)}><text x="{x}" y="{y}" font-size="14" xml:space="preserve">{p}</text></g>
<clipPath id="c{uid}">{clip}</clipPath>
<text x="{px}" y="{y}" font-size="14" fill="{INK}" clip-path="url(#c{uid})">{esc(cmd)}</text>'''
    return s, at + 0.35 + dur


def cursor(x, y, at):
    blink = "" if STATIC else f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{at:.2f}s" repeatCount="indefinite"/>'
    return f'<g{appear(at)}><rect x="{x}" y="{y - 13}" width="9" height="17" fill="{GREEN}">{blink}</rect></g>'


ASCII = """\
██████╗ ██╗  ██╗ █████╗ ██╗   ██╗███████╗███████╗██╗  ██╗
██╔══██╗██║  ██║██╔══██╗██║   ██║██╔════╝██╔════╝██║  ██║
██████╔╝███████║███████║██║   ██║█████╗  ███████╗███████║
██╔══██╗██╔══██║██╔══██║╚██╗ ██╔╝██╔══╝  ╚════██║██╔══██║
██████╔╝██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝""".split("\n")


def terminal():
    W, x = 1000, 36
    o = []
    y = 78
    pw, ph = 9, 17
    for dx, fill in [(3, DIM), (0, GREEN)]:
        cells = []
        for r, line in enumerate(ASCII):
            for c, ch in enumerate(line):
                if ch == "█":
                    cells.append(f'<rect x="{x + c * pw + dx}" y="{y - 14 + r * ph + dx}" width="{pw - 1}" height="{ph - 2}"/>')
        op = 0.55 if fill == DIM else 1
        o.append(f'<g fill="{fill}" opacity="{op}">{"".join(cells)}</g>')
    o.append(f'<text x="{x + 545}" y="{y + 5 * ph - 2}" font-size="12" fill="{DIM}">v0x327 · backend / infra / security</text>')
    y += 6 * ph + 34
    t = 0.4
    session = [
        ("whoami", [[("bhavesh mandhan", INK), (" — backend & infrastructure engineer, bengaluru", MUTED)]]),
        ("cat ~/.history", [[("oracle", AMBER), ("  ·  ", MUTED), ("hackerrank", AMBER), ("  ·  ", MUTED), ("delta force", AMBER)]]),
        ("grep -i belief ~/README", [[("> systems should stay correct when everything around them fails.", GREEN)]]),
        ("./after-hours --list", [[("ctf", INK), (" (forensics, reversing)", MUTED), ("  ·  ", MUTED), ("guitar", INK), ("  ·  ", MUTED), ("football", INK)]]),
    ]
    for n, (cmd, outs) in enumerate(session):
        s, t = prompt(x, y, cmd, t, n)
        o.append(s)
        y += 24
        t += 0.25
        for out in outs:
            spans = "".join(f'<tspan fill="{c}">{esc(txt)}</tspan>' for txt, c in out)
            o.append(f'<g{appear(t)}><text x="{x}" y="{y}" font-size="14" xml:space="preserve">{spans}</text></g>')
            y += 24
        y += 10
        t += 0.45
    s, _ = prompt(x, y, "", t, 99)
    o.append(s)
    o.append(cursor(x + len("bhavesh@github:~$ ") * CW, y, t + 0.1))
    return window(W, y + 30, "bhavesh@github: ~ — zsh", "\n".join(o))


def nmap():
    W, x = 1000, 36
    cols = [x, x + 120, x + 200, x + 330]
    rows = [("1337/tcp", "go", "services, concurrency, workers"),
            ("31337/tcp", "rust", "fast, correct command-line tools"),
            ("8000/tcp", "python", "fastapi, data pipelines"),
            ("4040/tcp", "kotlin", "android, generated api clients"),
            ("3000/tcp", "typescript", "web frontends"),
            ("9001/tcp", "c++", "algorithms, exploit scratchpads"),
            ("5432/tcp", "postgresql", "constraints as invariants, pgvector"),
            ("2376/tcp", "docker", "everything containerised, pinned"),
            ("6443/tcp", "kubernetes", "orchestration"),
            ("11434/tcp", "ollama", "local inference, data stays on box"),
            ("22/tcp", "ssh", "linux, all day")]
    o = []
    y = 70
    s, t = prompt(x, y, "nmap -sV -p- bhavesh0327", 0.3, 0)
    o.append(s)
    y += 30
    t += 0.3
    for line in ["Starting Nmap 7.95 ( https://nmap.org )",
                 "Nmap scan report for bhavesh0327 (github.com)",
                 "Host is up (0.00032s latency)."]:
        o.append(f'<g{appear(t)}><text x="{x}" y="{y}" font-size="14" fill="{MUTED}">{esc(line)}</text></g>')
        y += 22
        t += 0.12
    y += 14
    hdr = "".join(f'<text x="{cx}" y="{y}" font-size="14" font-weight="700" fill="{INK}">{h}</text>' for cx, h in zip(cols, ["PORT", "STATE", "SERVICE", "VERSION"]))
    o.append(f'<g{appear(t)}>{hdr}</g>')
    y += 26
    for port, svc, ver in rows:
        t += 0.14
        cells = (f'<text x="{cols[0]}" y="{y}" font-size="14" fill="{INK}">{port}</text>'
                 f'<text x="{cols[1]}" y="{y}" font-size="14" fill="{GREEN}">open</text>'
                 f'<text x="{cols[2]}" y="{y}" font-size="14" fill="{AMBER}">{esc(svc)}</text>'
                 f'<text x="{cols[3]}" y="{y}" font-size="14" fill="{MUTED}">{esc(ver)}</text>')
        o.append(f'<g{appear(t)}>{cells}</g>')
        y += 24
    y += 16
    t += 0.4
    for line, c in [("Service detection performed. 0 secrets exposed.", MUTED),
                    ("Nmap done: 1 IP address (1 host up) scanned in 0.33 seconds", GREEN)]:
        o.append(f'<g{appear(t)}><text x="{x}" y="{y}" font-size="14" fill="{c}">{esc(line)}</text></g>')
        y += 22
        t += 0.2
    return window(W, y + 22, "nmap — scan report", "\n".join(o))


def traceroute():
    W, x = 1000, 36
    hops = [("client", ["typed sdk", "from openapi"]),
            ("edge", ["tls · oidc+pkce", "rate limited"]),
            ("api", ["stateless", "idempotency keys"]),
            ("queue", ["durable jobs", "at-least-once"]),
            ("worker", ["sandboxed", "retry-safe"]),
            ("postgres", ["invariants as", "constraints"])]
    bw, bh, by = 128, 64, 150
    gap = (W - 2 * x - len(hops) * bw) / (len(hops) - 1)
    cy = by + bh / 2
    o = []
    s, t = prompt(x, 70, "traceroute --explain how-i-build", 0.3, 0)
    o.append(s)
    o.append(f'<g{appear(t + 0.2)}><text x="{x}" y="100" font-size="13" fill="{MUTED}">traceroute to production (stays correct), 6 hops max, every packet accounted for</text></g>')
    x0, x1 = x + bw / 2, W - x - bw / 2
    o.append(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{DIM}" stroke-width="1.5" stroke-dasharray="3 5"/>')
    if not STATIC:
        o.append(f'<path id="wire" d="M{x0} {cy} L{x1} {cy}" fill="none"/>')
        for i in range(3):
            o.append(f'<circle r="4" fill="{GREEN}"><animateMotion dur="4.5s" begin="{i * 1.5}s" repeatCount="indefinite"><mpath href="#wire"/></animateMotion></circle>')
    lat = ["0.21 ms", "0.48 ms", "1.02 ms", "0.33 ms", "2.71 ms"]
    for i, (name, notes) in enumerate(hops):
        bx = x + i * (bw + gap)
        last = i == len(hops) - 1
        o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{"#0f2a17" if last else BG}" stroke="{GREEN if last else BORDER}" stroke-width="1.4"/>')
        o.append(f'<text x="{bx + 12}" y="{by + 24}" font-size="11" fill="{DIM}">hop {i + 1:02d}</text>')
        o.append(f'<text x="{bx + 12}" y="{by + 47}" font-size="16" font-weight="700" fill="{GREEN if last else INK}">{name}</text>')
        for j, n in enumerate(notes):
            o.append(f'<text x="{bx + 4}" y="{by + bh + 26 + j * 18}" font-size="12" fill="{MUTED}">{esc(n)}</text>')
        if i < len(lat):
            o.append(f'<text x="{bx + bw + gap / 2}" y="{by - 10}" text-anchor="middle" font-size="11" fill="{DIM}">{lat[i]}</text>')
    ty = by + bh + 90
    o.append(f'<rect x="{x}" y="{ty}" width="{W - 2 * x}" height="44" rx="6" fill="none" stroke="{BORDER}" stroke-dasharray="4 4"/>')
    o.append(f'<text x="{x + 16}" y="{ty + 27}" font-size="13" fill="{INK}">tap<tspan fill="{MUTED}">  ── json logs  ·  request ids end to end  ·  traces  ·  replayable audit history</tspan></text>')
    for i in range(len(hops)):
        hx = x + i * (bw + gap) + bw / 2
        o.append(f'<line x1="{hx}" y1="{by + bh + 54}" x2="{hx}" y2="{ty}" stroke="{BORDER}" stroke-dasharray="2 4"/>')
    fy = ty + 80
    o.append(f'<g{appear(t + 0.6)}><text x="{x}" y="{fy}" font-size="14" fill="{GREEN}">trace complete: 6 hops, 0 dropped writes, 0 double charges.</text></g>')
    return window(W, fy + 26, "traceroute — how i build", "\n".join(o))


QUERY = """query($login: String!) { user(login: $login) {
  createdAt followers { totalCount }
  repositories(ownerAffiliations: OWNER, isFork: false, first: 100) { totalCount nodes {
    stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } } }
  contributionsCollection { totalCommitContributions restrictedContributionsCount
    contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }"""


def fetch(login, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": login})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["user"]


def longest_streak(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    return longest


MARKUP = {"HTML", "CSS", "SCSS", "Jupyter Notebook", "Makefile", "Dockerfile", "Procfile"}


def telemetry(u):
    W, x = 1000, 36
    cc = u["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    best = longest_streak(days)
    peak = max((d["contributionCount"] for d in days), default=0) or 1
    repos = u["repositories"]["nodes"]
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            if e["node"]["name"] not in MARKUP:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:7]
    years = datetime.date.today().year - int(u["createdAt"][:4])
    o = []
    s, t = prompt(x, 70, "btop --user bhavesh0327 --since 1y", 0.3, 0)
    o.append(s)
    t += 0.2
    facts = [("uptime", f"{years} years on github"),
             ("contribs", f'{cc["contributionCalendar"]["totalContributions"]} in the last year'),
             ("commits", f'{cc["totalCommitContributions"] + cc["restrictedContributionsCount"]}'),
             ("repos", f'{u["repositories"]["totalCount"]}'),
             ("streak", f"{best} days, longest run"),
             ("busiest", f"{peak} contributions in a day"),
             ("stars", f'{sum(r["stargazerCount"] for r in repos)}'),
             ("followers", f'{u["followers"]["totalCount"]}')]
    y = 112
    for k, v in facts:
        o.append(f'<g{appear(t)}><text x="{x}" y="{y}" font-size="14" xml:space="preserve"><tspan fill="{GREEN}">{k:<11}</tspan><tspan fill="{INK}">{esc(v)}</tspan></text></g>')
        y += 24
        t += 0.08
    lx, y = 500, 112
    o.append(f'<text x="{lx}" y="{y - 30}" font-size="11" fill="{DIM}" letter-spacing="1.5">LANGUAGES · BY BYTES</text>')
    for name, size in top:
        pct = size / total
        filled = max(1, round(pct * 20))
        segs = "".join(f'<rect x="{lx + 110 + i * 12}" y="{y - 12}" width="10" height="14" rx="1" fill="{GREEN if i < filled else "#21262d"}"/>' for i in range(20))
        o.append(f'<g{appear(t)}><text x="{lx}" y="{y}" font-size="14" fill="{AMBER}">{esc(name.lower())}</text>{segs}'
                 f'<text x="{lx + 360}" y="{y}" font-size="13" fill="{MUTED}">{pct * 100:5.1f}%</text></g>')
        y += 24
        t += 0.08
    hy = 112 + 7 * 24 + 40
    o.append(f'<text x="{x}" y="{hy}" font-size="11" fill="{DIM}" letter-spacing="1.5">CONTRIBUTIONS · LAST 52 WEEKS</text>')
    shades = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    hy += 14
    for wi, w in enumerate(weeks):
        cells = []
        for d in w["contributionDays"]:
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
            wd = datetime.date.fromisoformat(d["date"]).isoweekday() % 7
            cells.append(f'<rect x="{x + wi * 17}" y="{hy + wd * 17}" width="13" height="13" rx="2" fill="{shades[lvl]}"/>')
        o.append(f'<g{appear(t + wi * 0.02)}>{"".join(cells)}</g>')
    ly = hy + 7 * 17 + 22
    legend = "".join(f'<rect x="{W - x - 128 + i * 17}" y="{ly - 11}" width="13" height="13" rx="2" fill="{c}"/>' for i, c in enumerate(shades))
    o.append(f'<text x="{W - x - 168}" y="{ly}" font-size="11" fill="{MUTED}">less</text>{legend}<text x="{W - x - 40}" y="{ly}" font-size="11" fill="{MUTED}" dx="8">more</text>')
    o.append(f'<text x="{x}" y="{ly}" font-size="11" fill="{DIM}">refreshed {datetime.date.today().isoformat()} by a cron job, naturally</text>')
    return window(W, ly + 28, "btop — telemetry", "\n".join(o))


for name, fn in [("terminal", terminal), ("nmap", nmap), ("traceroute", traceroute)]:
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(fn())

token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if token:
    with open(os.path.join(OUT, "telemetry.svg"), "w") as f:
        f.write(telemetry(fetch("Bhavesh0327", token)))
