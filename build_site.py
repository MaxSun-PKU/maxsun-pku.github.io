"""Generate a dependency-free academic homepage from content.json."""
from pathlib import Path
import json
import html

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
DATA = json.loads((ROOT / 'content.json').read_text())
E = html.escape
PAGES = [('about', 'About', ''), ('publications', 'Publications', 'publications/'), ('research', 'Research', 'research/'), ('cv', 'CV', 'cv/'), ('more', 'More', 'more/')]
ICONS = {
    'email': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m3 5 9 7 9-7"/>',
    'scholar': '<path d="m2 9 10-5 10 5-10 5-10-5Zm4 3v6c3 2 9 2 12 0v-6M22 9v8"/>',
    'orcid': '<circle cx="12" cy="12" r="10"/><path d="M8 10v7M8 7v.5M12 10h2a3.5 3.5 0 0 1 0 7h-2z"/>',
    'github': '<path d="M9 21v-4c-4 1-4-2-6-2m12 6v-4c0-1 .5-2 1-2 4-1 5-3 5-6 0-1-.5-2-1-3 0-1 0-2-.5-3-2 0-3 1-4 1-2-.5-4-.5-6 0-1 0-2-1-4-1-.5 1-.5 2-.5 3-.5 1-1 2-1 3 0 3 1 5 5 6 .5 0 1 1 1 2"/>',
    'download': '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>'
}

def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

def bibtex(pub):
    authors = {
        'Sun2026Hosts': 'Sun, Shengxiu and Jiang, Linhua and Pan, Zhiwei and Siudek, Malgorzata and others',
        'Sun2026ChangingLook': 'Sun, Shengxiu and Jiang, Linhua and Guo, Wei-Jian and Bosman, Sarah E. I. and Pan, Zhiwei',
        'Sun2026Paschen': 'Sun, Shengxiu and Bosman, Sarah E. I. and Davies, Frederick B. and Protušová, Klaudia and Spina, Benedetta and Jiang, Linhua and Jiang, Danyang',
        'SunKinematics': 'Sun, Shengxiu and Jiang, Linhua and Bosman, Sarah E. I. and Cheng, Yang',
        'Jiang2025Reionization': 'Jiang, Danyang and Jiang, Linhua and Sun, Shengxiu and others',
        'Pan2025Iron': 'Pan, Zhiwei and Jiang, Linhua and Guo, Wei-Jian and Sun, Shengxiu and others',
        'Jiang2026Cosmos': 'Jiang, Danyang and Jiang, Linhua and Fu, Shuqi and Zhang, Z. and Chen, J. and Pan, Zhiwei and Sun, Shengxiu and others',
        'Chen2025SOM': 'Chen, J. and Jiang, Linhua and Sun, Shengxiu and others',
        'Guo2025BroadLines': 'Guo, Wei-Jian and Fawcett, V. A. and Siudek, Malgorzata and Li, Y.-R. and Cheng, C. and Panda, S. and Pan, Zhiwei and Sun, Shengxiu and others',
        'Yin2026QLF': 'Yin, Gaocheng and Jiang, Linhua and Pan, Zhiwei and Martini, Paul and Guo, Wei-Jian and Zou, S. and Sun, Shengxiu and others'
    }
    fields = {'title': '{' + pub['title'] + '}', 'author': authors[pub['id']], 'year': str(pub['year'])}
    if pub.get('doi'):
        fields['doi'] = pub['doi']
        fields['journal'] = 'Nature Astronomy' if 'Nature' in pub['venue'] else 'The Astrophysical Journal'
        parts = pub['venue'].split(', ')
        if len(parts) == 3:
            fields['volume'], fields['pages'] = parts[1:]
    if pub.get('arxiv'):
        fields['eprint'] = pub['arxiv']
        fields['archivePrefix'] = 'arXiv'
    if pub['status'] != 'Published':
        fields['note'] = pub['venue']
    kind = 'article' if pub.get('doi') else 'misc'
    return '@' + kind + '{' + pub['id'] + ',\n' + ',\n'.join(f'  {key} = {{{value}}}' for key, value in fields.items()) + '\n}'

def puburl(pub):
    if pub.get('doi'):
        return 'https://doi.org/' + pub['doi']
    if pub.get('arxiv'):
        return 'https://arxiv.org/abs/' + pub['arxiv']
    return None

def authors(pub):
    return E(pub['authors']).replace('Sun, S.', '<strong>Sun, S.</strong>')

def brief_pub(pub):
    title = E(pub['title'])
    if puburl(pub):
        title = f'<a href="{puburl(pub)}">{title}</a>'
    role = 'First author' if pub['group'] == 'first' else pub['position']
    links = []
    if pub.get('doi'):
        links.append(f'<a href="https://doi.org/{pub["doi"]}">DOI</a>')
    if pub.get('arxiv'):
        links.append(f'<a href="https://arxiv.org/abs/{pub["arxiv"]}">arXiv</a>')
    return f'<article class="brief-pub"><h3>{title}</h3><p class="selected-authors">{authors(pub)}</p><p class="selected-venue">{E(pub["venue"])}</p><p class="publication-note">{E(role)} · {E(pub["status"])}' + (' · ' + ' · '.join(links) if links else '') + '</p></article>'

def page_shell(page, content):
    prefix = '' if page == 'about' else '../'
    nav = ''.join(f'<a href="{prefix}{path or "index.html"}"' + (' aria-current="page"' if key == page else '') + f'>{label}</a>' for key, label, path in PAGES)
    title = 'Shengxiu Sun | Astronomy, Peking University' if page == 'about' else next(label for key, label, _ in PAGES if key == page) + ' · Shengxiu Sun'
    desc = 'Shengxiu Sun is a PhD candidate at Peking University studying AGN–host galaxy co-evolution, quasar spectroscopy, and interpretable machine learning.'
    canonical = DATA['site_url'].rstrip('/') + '/' + next(path for key, _, path in PAGES if key == page)
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'Person', 'name': DATA['name'], 'url': DATA['site_url'], 'image': DATA['site_url'].rstrip('/') + '/assets/shengxiu-sun-portrait.webp', 'jobTitle': DATA['role'], 'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Peking University'}, 'email': 'mailto:' + DATA['email'], 'sameAs': [DATA['scholar'], DATA['github'], 'https://orcid.org/' + DATA['orcid']]}, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#ffffff"><meta name="robots" content="index,follow"><link rel="canonical" href="{E(canonical)}"><title>{E(title)}</title><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{E(canonical)}"><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/app.js" defer></script><script type="application/ld+json">{schema}</script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="masthead"><div class="topbar"><a class="brand" href="{prefix}index.html">Shengxiu Sun</a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav">Menu</button><nav class="nav" id="main-nav" aria-label="Main navigation">{nav}</nav></div></header>
<div class="layout"><aside class="profile" aria-label="About Shengxiu Sun"><a class="profile-photo" href="{prefix}assets/shengxiu-sun-portrait.webp" aria-label="View portrait of Shengxiu Sun"><img src="{prefix}assets/shengxiu-sun-portrait.webp" alt="Shengxiu Sun" width="768" height="768"></a><h2>Shengxiu Sun</h2><p class="role">PhD candidate in Astronomy<br>Kavli Institute for Astronomy<br>and Astrophysics</p><div class="place"><span class="institution-line">Peking University<br></span>Beijing, China</div><div class="profile-links"><a class="email-link" href="mailto:{DATA['email']}">{icon('email')}Email</a><a href="{E(DATA['scholar'])}">{icon('scholar')}Google Scholar</a><a href="https://orcid.org/{DATA['orcid']}">{icon('orcid')}ORCID</a><a href="{DATA['github']}">{icon('github')}GitHub</a><a href="{prefix}downloads/Shengxiu_Sun_CV.pdf">{icon('download')}Curriculum vitae</a></div></aside><main id="main">{content}</main></div>
<footer class="footer"><div class="footer-inner"><span>© 2026 Shengxiu Sun · <a href="mailto:{DATA['email']}">{DATA['email']}</a></span><span>Last updated {DATA['updated']}</span></div></footer></body></html>'''

ABOUT = '''<header class="page-title"><h1>About me</h1></header><div class="intro"><p>I am a PhD candidate in Astronomy at the <a href="https://kiaa.pku.edu.cn/">Kavli Institute for Astronomy and Astrophysics (KIAA), Peking University</a>, supervised by Prof. Linhua Jiang. I expect to complete my PhD in 2027.</p><p>My research focuses on <strong>AGN–host galaxy co-evolution</strong>. I use optical and near-infrared spectroscopy, high-resolution imaging, and forward modeling to recover quasar host properties and study black-hole growth. My recent work covers spectrophotometric decomposition, changing-look AGNs, Paschen-line black-hole mass calibration, and host stellar kinematics.</p><p>I received my BSc in Astronomy from Nanjing University in 2022 and was an exchange PhD student at Heidelberg University’s Institute for Theoretical Physics from September 2025 to September 2026.</p><p><a href="downloads/Shengxiu_Sun_CV.pdf">CV (PDF)</a> · <a href="research/">Research</a> · <a href="mailto:sxsun@stu.pku.edu.cn">sxsun@stu.pku.edu.cn</a></p></div>'''
ABOUT += '<section class="section selected-work"><div class="section-heading"><h2>Selected publications</h2><a href="publications/">All publications →</a></div>' + ''.join(brief_pub(pub) for pub in DATA['publications'][:3]) + brief_pub(DATA['publications'][4]) + '</section>'

RESEARCH = '''<header class="page-title"><h1>Research</h1><p class="page-lead">How do supermassive black holes grow with their galaxies? I approach this question by separating the light we observe, calibrating the physical scales, and testing the connection across different populations and cosmic epochs.</p><a class="text-link" href="../downloads/Shengxiu_Sun_Research_Summary.pdf">Download research summary ↓</a></header><nav class="anchor-nav" aria-label="Research topics"><a href="#quasar-hosts">Quasar hosts</a><a href="#changing-look">Changing-look AGNs</a><a href="#paschen">Black-hole masses</a><a href="#kinematics">Stellar kinematics</a><a href="#cosmic-dawn">Cosmic dawn</a></nav>
<section class="research-section" id="quasar-hosts"><h2 class="project-title">Quasar host galaxies with DESI &amp; HSC</h2><p class="project-sub">First-author work · ApJ, 1004, 13 (2026)</p><p>A bright AGN can overwhelm the stellar light needed to understand its host. I developed an iterative spectrophotometric decomposition that combines DESI spectra with Subaru/HSC images for 1,083 extended type-1 quasars at 0.1 &lt; z &lt; 1.</p><p>PSF-subtracted imaging constrains the host flux within the spectroscopic aperture; spectral fitting constrains the stellar population and nuclear emission. Together, these measurements reduce the degeneracy between the two components and recover host star formation, stellar mass, and black-hole–stellar-mass relations.</p><div class="project-finding"><p><strong>Main result.</strong> These extended-quasar hosts are predominantly quiescent, and about 23% show post-starburst signatures. Active black-hole growth can coexist with weak current star formation. The morphology selection favours prominent hosts, so the result describes this selected population.</p></div><div class="project-links"><a href="https://doi.org/10.3847/1538-4357/ae6e35">Journal article ↗</a><a href="https://arxiv.org/abs/2607.28732">arXiv ↗</a><a href="https://zenodo.org/records/17085386">Supplementary data ↗</a></div></section>
<section class="research-section" id="changing-look"><h2 class="project-title">Changing-look AGNs as a physical laboratory</h2><p class="project-sub">First-author preprint · Submitted to ApJ</p><p>Changing-look AGNs change their continuum and broad lines over years, while their host stellar populations remain effectively stable. I extended the decomposition to paired DESI and SDSS spectra of 105 changing-look AGNs, using HSC photometry to account for the different fibre apertures.</p><p>The model shares a stellar population across epochs while allowing nuclear emission to vary. A faint epoch can reveal the host; a bright epoch constrains the AGN. Their consistency provides a direct check on component separation.</p><div class="project-finding"><p><strong>Main result.</strong> Among 82 extended changing-look AGNs and a comparison sample matched in redshift and stellar mass, post-starburst fractions are 35.4% and 18.3%. The quiescent fractions do not differ clearly. Together with the rapid nuclear transitions, this favours changes in central accretion as the main driver.</p></div><div class="project-links"><a href="https://arxiv.org/abs/2607.28735">Read the preprint ↗</a></div></section>
<section class="research-section" id="paschen"><h2 class="project-title">Near-infrared black-hole mass tracers</h2><p class="project-sub">First-author preprint · Submitted to A&amp;A</p><p>When optical broad lines are attenuated or unavailable, near-infrared Paschen lines offer complementary access to black-hole masses. I reduced and analysed LBT/LUCI spectra of 27 SDSS reverberation-mapping quasars, combining them with archival Paschen measurements of AGNs with reverberation masses.</p><p>We anchor single-epoch Paα and Paβ estimators directly to reverberation mapping, and test the dependence on line profiles, luminosity definitions, and virial exponents.</p><div class="project-finding"><p><strong>Main result.</strong> The fiducial intrinsic scatters are 0.28 dex for Paα and 0.32 dex for Paβ within the calibration sample. The absolute mass scale remains subject to the reverberation-mapping virial factor.</p></div><div class="project-links"><a href="https://arxiv.org/abs/2608.24645">Read the preprint ↗</a></div></section>
<section class="research-section" id="kinematics"><h2 class="project-title">Stellar kinematics with forward-modeled spectra</h2><p class="project-sub">First-author manuscript · In preparation</p><p>Host absorption features are diluted by AGN continuum and emission lines. I developed a neural network trained on 220,000 forward-modeled spectra to estimate stellar velocity dispersion, reconstruct the stellar and nuclear components, and report calibrated uncertainties.</p><p>Independent mock tests and comparisons with SDSS and higher-resolution Keck spectra identify useful regimes and measurement biases. Confidence criteria assess host information and reconstruction quality, including limits set by spectral resolution.</p><figure class="research-figure"><a href="../assets/spectral-reconstruction.png"><img src="../assets/spectral-reconstruction.png" alt="SDSS spectrum and reconstructed host, AGN, and total model, with residuals and two zoomed stellar absorption windows" width="1461" height="1059"></a><figcaption>Recovering the host absorption spectrum beneath nuclear light. The observed SDSS spectrum, total model, host, AGN, and residuals can be inspected together. Figure from Sun et al., manuscript in preparation; click to view at full size.</figcaption></figure><div class="project-finding"><p><strong>Main result.</strong> Of 399 nearby broad-line AGNs, 159 pass the adopted confidence criteria. Their fitted M<sub>BH</sub>–σ<sub>★</sub> slope is 4.74 ± 0.55 under the adopted uncertainties. The normalization depends on the virial mass scale and the selected host population.</p></div><figure class="research-figure narrow"><a href="../assets/host-kinematics.png"><img src="../assets/host-kinematics.png" alt="Black-hole mass versus inferred host velocity dispersion for low-, intermediate-, and high-confidence AGN measurements, with a fitted relation and virial-mass distribution" width="785" height="1329"></a><figcaption>The black-hole mass–dispersion relation and mass distribution, shown by confidence group. Figure from Sun et al., manuscript in preparation.</figcaption></figure><div class="project-links"><a href="../publications/#SunKinematics">Manuscript details →</a></div></section>
<section class="research-section" id="cosmic-dawn"><h2 class="project-title">AGN populations at cosmic dawn</h2><p class="project-sub">Collaborative work · Nature Astronomy (2025) · 3rd author</p><p>I contributed to a JWST/NIRCam study of AGNs at 7.15 ≤ z ≤ 7.75. Decomposing rest-frame ultraviolet images into unresolved and extended components connects the same component-separation problem to the origin of the ionizing photons that reionized the Universe.</p><div class="project-finding"><p><strong>Main result.</strong> Even assigning all unresolved light to AGNs gives an upper bound of about one third of the ionizing photons required at z ≈ 7.5. This conservative bound rules out AGNs as the dominant source in the studied population.</p></div><div class="project-links"><a href="https://doi.org/10.1038/s41550-025-02676-7">Journal article ↗</a></div></section>
<section class="future"><h2>Future research interests</h2><p>I am interested in spatially resolved near-infrared spectroscopy of quasar hosts and environments, connecting JWST observations to wide-area Euclid imaging and LBT follow-up. This would extend host-aware measurements to companion galaxies, extended gas, and the earliest stages of black-hole growth.</p></section>'''

def publications():
    out = '''<header class="page-title"><h1>Publications</h1><p class="page-lead">Publications and manuscripts are grouped by authorship. Submitted papers and work in preparation are labeled explicitly.</p><div class="actions"><a class="text-link" href="../downloads/publications.bib" download>Download BibTeX ↓</a><a class="text-link" href="''' + E(DATA['scholar']) + '''">Google Scholar ↗</a></div></header><div class="filterbar" role="group" aria-label="Filter by authorship"><span class="filter-label">Authorship</span><button class="filter" data-filter="all" aria-pressed="true">All work</button><button class="filter" data-filter="first" aria-pressed="false">First author</button><button class="filter" data-filter="collaborative" aria-pressed="false">Collaborative</button></div><div class="filterbar status-filters" role="group" aria-label="Filter by publication status"><span class="filter-label">Status</span><button class="status-filter filter" data-status-filter="all" aria-pressed="true">All</button><button class="status-filter filter" data-status-filter="Published" aria-pressed="false">Published</button><button class="status-filter filter" data-status-filter="Submitted" aria-pressed="false">Preprints</button><button class="status-filter filter" data-status-filter="In preparation" aria-pressed="false">In preparation</button></div><p class="result-count" aria-live="polite">Showing 10 entries</p>'''
    for group, heading in [('first', 'First-author papers and manuscripts'), ('collaborative', 'Collaborative publications')]:
        out += f'<section class="pub-group" data-group="{group}"><h2 class="pub-section-title">{E(heading)}</h2>'
        for pub in sorted(DATA['publications'], key=lambda item: -item['year']):
            if pub['group'] != group:
                continue
            title = E(pub['title'])
            if puburl(pub):
                title = f'<a href="{puburl(pub)}">{title}</a>'
            cls = 'submitted' if pub['status'] == 'Submitted' else 'preparation' if pub['status'] == 'In preparation' else ''
            out += f'<article class="publication" id="{pub["id"]}" data-group="{group}" data-status="{E(pub["status"])}"><div class="pub-top"><span>{pub["year"]}</span><span class="status {cls}">{E(pub["status"])}</span>'
            out += '<span class="authorship">' + ('First author' if group == 'first' else E(pub['position'])) + '</span>'
            out += f'</div><h3>{title}</h3><p class="pub-authors">{authors(pub)}</p><p class="pub-venue">{E(pub["venue"])}</p>'
            if pub.get('summary'):
                out += '<p class="pub-summary">' + E(pub['summary']) + '</p>'
            out += '<div class="pub-actions">'
            if pub.get('doi'):
                out += f'<a href="https://doi.org/{pub["doi"]}">DOI ↗</a>'
            if pub.get('arxiv'):
                out += f'<a href="https://arxiv.org/abs/{pub["arxiv"]}">arXiv ↗</a>'
            if pub.get('project'):
                out += f'<a href="../research/#{pub["project"]}">Research overview →</a>'
            out += f'<button class="cite-button" type="button" data-citation="{E(bibtex(pub), quote=True)}" aria-label="Cite {E(pub["title"], quote=True)}">BibTeX</button></div></article>'
        out += '</section>'
    return out + '''<dialog class="citation-dialog" aria-labelledby="citation-title"><h2 id="citation-title">BibTeX citation</h2><pre tabindex="0"></pre><div class="dialog-actions"><button class="button copy-citation" type="button">Copy BibTeX</button><button class="close-dialog" type="button">Close</button></div><p class="copy-status" aria-live="polite"></p></dialog>'''

CV = '''<header class="page-title"><h1>Curriculum vitae</h1><p class="page-lead">Observational astronomy, AGN–host galaxy co-evolution, and uncertainty-aware inference.</p><div class="actions"><a class="button" href="../downloads/Shengxiu_Sun_CV.pdf">Download full CV <span aria-hidden="true">↓</span></a><a class="text-link" href="../publications/">Publications →</a></div></header>
<section class="cv-section"><h2>Education</h2><ol class="timeline"><li><div class="date">2022–present</div><div><h3>PhD candidate in Astronomy</h3><p>Kavli Institute for Astronomy and Astrophysics, Peking University<br>Supervisor: Prof. Linhua Jiang · Expected completion: 2027</p></div></li><li><div class="date">Sep 2025–<br>Sep 2026</div><div><h3>Exchange PhD student</h3><p>Institute for Theoretical Physics, Heidelberg University</p></div></li><li><div class="date">Sep 2018–<br>Jun 2022</div><div><h3>BSc in Astronomy</h3><p>School of Astronomy and Space Science, Nanjing University</p></div></li></ol></section>
<section class="cv-section"><h2>Research experience &amp; skills</h2><dl class="skills-grid"><dt>Observations</dt><dd>LBT/LUCI near-infrared spectroscopy; DESI and SDSS spectroscopy; Subaru/HSC imaging; JWST/NIRCam science analysis.</dd><dt>Analysis</dt><dd>Optical and near-infrared data reduction; PSF-aware image and spectrum decomposition; stellar-population and emission-line modeling; reverberation-mapping and single-epoch mass calibration.</dd><dt>Inference</dt><dd>Forward modeling, mock-data and injection-recovery validation, calibrated uncertainties, and neural networks for astronomical spectra.</dd><dt>Computing</dt><dd>Python, NumPy, SciPy, Astropy, PyTorch, FSPS, Matplotlib; reproducible HPC workflows.</dd><dt>Developing interests</dt><dd>NIRSpec IFU science planning, Euclid morphology, and spatially resolved quasar environments.</dd></dl></section>
<section class="cv-section"><h2>Teaching</h2><ol class="timeline"><li><time>2025</time><div><h3>Galaxy Physics</h3><p>Teaching Assistant · Peking University</p></div></li><li><time>2024</time><div><h3>Fundamental Astronomy</h3><p>Teaching Assistant · Peking University</p></div></li><li><time>2024</time><div><h3>Astronomical Data Processing</h3><p>Teaching Assistant · Peking University</p></div></li></ol></section>
<section class="cv-section"><h2>Honors &amp; scholarships</h2><ol class="timeline"><li><time>2025</time><div><h3>China Scholarship Council Scholarship</h3><p>State-Sponsored Overseas Study · Heidelberg University</p></div></li><li><time>2022</time><div><h3>Mercedes-Benz Scholarship</h3></div></li><li><time>2022</time><div><h3>Outstanding Research Award</h3></div></li></ol></section><section class="contact-block"><p>Selected conference presentations are listed on the <a href="../more/">More page</a>. The downloadable CV includes the selected publication record and author positions.</p></section>'''

MORE = '''<header class="page-title"><h1>Talks &amp; teaching</h1></header><figure class="personal-photo"><a href="../assets/shengxiu-sun-outdoors.webp"><img src="../assets/shengxiu-sun-outdoors.webp" alt="Shengxiu Sun by the sea, standing beside a natural rock arch" width="1600" height="1067"></a></figure><section class="section"><h2>Selected talks</h2><article class="talk"><div class="talk-meta">2026 · Spotlight talk</div><h3>Exploring AGN host galaxies with DESI</h3><p>DESI Collaboration Meeting · Durham University, UK</p></article><article class="talk"><div class="talk-meta">2025 · Talk</div><h3>DESI CL-AGNs viewed in spectrophotometric decomposition</h3><p>CSST Annual Science Meeting · Kunming, China</p></article><article class="talk"><div class="talk-meta">2025 · Talk</div><h3>Exploring the properties of quasar host galaxies with spectrophotometric decomposition</h3><p>27th Guo Shoujing Symposium on Frontiers in Galaxy Cosmology · Changsha, China</p></article><article class="talk"><div class="talk-meta">2024 · Talk</div><h3>Exploring the properties of quasar host galaxies with spectrophotometric decomposition</h3><p>Probing the Genesis of Supermassive Black Holes · Kavli IPMU, Kashiwa, Japan</p></article></section>
<section class="section"><h2>Teaching</h2><p>I have been a teaching assistant at Peking University for <strong>Galaxy Physics</strong> (2025), <strong>Fundamental Astronomy</strong> (2024), and <strong>Astronomical Data Processing</strong> (2024).</p></section>
<section class="section"><h2>Useful astronomy resources</h2><div class="resource-grid"><div class="resource"><a href="https://ui.adsabs.harvard.edu/">NASA ADS ↗</a><p>Search the astrophysics literature and follow related research.</p></div><div class="resource"><a href="https://arxiv.org/archive/astro-ph">arXiv / astro-ph ↗</a><p>Read the latest astrophysics preprints.</p></div><div class="resource"><a href="https://data.desi.lbl.gov/">DESI data ↗</a><p>Public spectroscopic survey data and documentation.</p></div><div class="resource"><a href="https://hsc-release.mtk.nao.ac.jp/">Subaru HSC data releases ↗</a><p>Wide-field imaging for galaxy and quasar-host studies.</p></div><div class="resource"><a href="https://mast.stsci.edu/">MAST ↗</a><p>Access space-telescope observations, including JWST.</p></div><div class="resource"><a href="https://www.astropy.org/">Astropy ↗</a><p>Python tools for astronomical data and analysis.</p></div></div></section>
<section class="contact-block"><h2>Contact</h2><p>Shengxiu Sun<br>Kavli Institute for Astronomy and Astrophysics<br>Peking University, Beijing, China</p><a class="text-link" href="mailto:sxsun@stu.pku.edu.cn">sxsun@stu.pku.edu.cn ↗</a></section>'''

content = {'about': ABOUT, 'research': RESEARCH, 'publications': publications(), 'cv': CV, 'more': MORE}
for key, label, path in PAGES:
    directory = DIST / path
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'index.html').write_text(page_shell(key, content[key]))
(DIST / 'downloads/publications.bib').write_text('\n\n'.join(bibtex(pub) for pub in DATA['publications']) + '\n')
(DIST / '.nojekyll').touch()
site_url = DATA['site_url'].rstrip('/')
(DIST / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + site_url + '/sitemap.xml\n')
urls = ''.join('<url><loc>' + site_url + '/' + path + '</loc><lastmod>' + DATA['updated_iso'] + '</lastmod></url>' for _, _, path in PAGES)
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
print('Generated 5 pages and 10 BibTeX entries.')
