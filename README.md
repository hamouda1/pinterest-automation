# 📌 Pinterest Automation Cloud Engine

Automated, high-converting Pinterest pin generation powered by **Playwright**, **HTML5/CSS3 Grid & Flexbox**, and **GitHub Actions**.

## 🚀 Features
- **24/7 Cloud Execution:** Runs on GitHub's enterprise cloud infrastructure (7GB RAM) without requiring local PC to stay awake.
- **Smart Image Loading:** JavaScript event listeners (`img.complete` check) ensure zero broken or half-loaded Amazon images.
- **Automated A/B Testing:** Multi-variation generation (`variations: 2`) with distinct color palettes and templates.
- **Single & Collage Support:** Seamlessly bifurcates between Single Product Pins and Multi-Item Collections (Spotlight 1+3 & Quad 2x2).
- **Free Global CDN:** Every pin published into `output/` gets an instant public CDN link:
  `https://raw.githubusercontent.com/hamouda1/pinterest-automation/main/output/{filename}.jpg`

## 📁 Repository Structure
```text
├── .github/workflows/main.yml  # GitHub Actions automated workflow
├── templates/                  # 5 responsive HTML/CSS pin templates
├── output/                     # Generated high-converting JPEG pins
├── products.json               # Input product catalog and collections
└── generate_pins.py            # Async Playwright generation script
```

## ⚡ Manual Execution
You can trigger a cloud generation round anytime by navigating to the **Actions** tab in this repository, selecting **Pinterest Pins Cloud Generator**, and clicking **Run workflow**.
