# PokemonCardChecker

A full‑stack web application that allows users to manage a Pokémon card collection, scan cards using a phone camera, and retrieve live market prices in real time.

This project uses **Webscraping**, **APIs**, **pHashing** to help ensure accurate pricing and image recognition

---

## Features

* Add Pokémon cards manually by name and number
* Scan physical cards using a phone camera
* Identify cards using perceptual image hashing (pHash)
* Confidence‑based card recognition with fallback suggestions
* Fetch live ungraded and PSA 10 prices via web scraping
* Store collections and wishlists persistently
* Clean, responsive frontend UI

---

## Tech Stack

**Backend**

* Python
* Flask
* SQLAlchemy
* Playwright (async web scraping)
* OpenCV
* Pillow
* imagehash

**Frontend**

* HTML
* CSS
* JavaScript

---

## How It Works

### Card Recognition

1. User uploads an image or scans a card using their phone camera
2. OpenCV detects and extracts potential card regions from the image
3. Each candidate is normalised and resized
4. A perceptual hash (pHash) is generated
5. The hash is compared against a prebuilt hash database
6. If the distance is below a confidence threshold, the card is automatically identified
7. If confidence is low, the top matches can be presented for manual selection

This approach allows recognition even with:

* Background clutter
* Different lighting conditions
* Slight perspective distortion

---

### Live Price Scraping

* Uses Playwright to automate a real marketplace
* Searches for the card by name and number
* Retrieves:

  * Ungraded market price
  * PSA 10 graded price
  * Official product image

#### Performance Optimisations

* Reduced DOM traversal and element lookups
* Reused browser contexts
* Cached frequent results in memory

**Performance Results:**

* Initial scrape: ~2 seconds
* Cached scrape: as fast as ~500ms

---

## Database Design

* Relational models for:

  * Card collection
  * Wishlist
* Stores:

  * Card metadata
  * Pricing information
  * Card images
* Implemented using SQLAlchemy

---

## Why This Project Matters

This project demonstrates:

* Full‑stack development skills
* Asynchronous programming
* Real‑world web scraping
* Computer vision and image matching
* Performance optimisation
* Clean UI/UX integration

It was built to solve a real personal use case by combining two hobbies: **software development and Pokémon card collecting**.

---

## Future Improvements

* Multiple marketplace support
* Price history tracking
* Cloud deployment
* User authentication
* Mobile‑first scanning improvements

---

## Author

Billy

---

If you’re a recruiter or developer reviewing this project and would like more details, feel free to reach out.
