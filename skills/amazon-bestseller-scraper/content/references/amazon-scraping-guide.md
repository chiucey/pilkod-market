# 亞馬遜爬蟲技術參考

## Amazon Bestseller URL 結構

```
https://www.amazon.com/gp/bestsellers/{category}/
```

### 常見品類 URL

| 品類 | URL | 子類目 |
|------|-----|--------|
| 電子產品 | `/gp/bestsellers/electronics/` | 耳機、相機、筆電 |
| 服飾 | `/gp/bestsellers/apparel/` | 男裝、女裝、童裝 |
| 圖書 | `/gp/bestsellers/books/` | 暢銷書、小說、商業 |
| 廚房 | `/gp/bestsellers/kitchen/` | 鍋具、小家電、餐具 |
| 玩具 | `/gp/bestsellers/toys-and-games/` | 桌遊、教育玩具 |
| 運動 | `/gp/bestsellers/sports/` | 健身、戶外、球類 |
| 美容 | `/gp/bestsellers/beauty/` | 護膚、彩妝、香水 |
| 母嬰 | `/gp/bestsellers/baby-products/` | 尿布、推車、玩具 |
| 汽車 | `/gp/bestsellers/automotive/` | 車用品、配件 |
| 家居 | `/gp/bestsellers/home-garden/` | 家具、花園 |

## 頁面解析要點

### 暢銷榜商品元素

每個商品通常位於 `#1` 這類排名標記的元素附近，結構為：

```html
<li data-component="product">
  <span class="zg-bdg-text">#1</span>
  <a class="a-link-normal" href="...">
    <img src="product-image.jpg">
  </a>
  <div class="p13n-sc-truncate">Product Name</div>
</li>
```

### 關鍵選擇器

| 目標 | CSS 選擇器 |
|------|-----------|
| 商品列表項 | `#zg-center-list li` |
| 排名 | `.zg-bdg-text` |
| 商品名稱 | `.p13n-sc-truncate` |
| 圖片 URL | `.a-column img[src]` |
| 詳情連結 | `.a-link-normal` |

## 反爬應對策略

### 請求頻率控制

- 請求間隔：2-3 秒
- 批次處理：每批 10-20 個請求
- 隨機延遲：增加隨機性避免規律檢測

### User-Agent 輪換

常用 User-Agent 範例：

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
```

### 失敗處理

| 錯誤類型 | 處理方式 |
|----------|----------|
| 403 Forbidden | 更換 User-Agent，等待後重試 |
| 429 Too Many Requests | 增加延遲時間，降級請求頻率 |
| Timeout | 重試最多 3 次，指數退避 |
| 解析失敗 | 記錄原始 HTML，人工檢查 |

## 數據存儲建議

### 輸出格式

**JSON（推薦）**
```json
{
  "category": "electronics",
  "scrape_date": "2026-03-26",
  "products": [
    {
      "rank": 1,
      "name": "Product Name",
      "image_url": "https://...",
      "product_url": "https://amazon.com/...",
      "asin": "B0XXXXXX"
    }
  ]
}
```

**CSV**
```csv
rank,name,image_url,product_url,asin
1,"Product Name","https://...","https://...",B0XXXXXX
```

## 道德規範

1. **遵守 robots.txt**：檢查 `/robots.txt` 允許的爬取路徑
2. **限速請求**：避免對伺服器造成負擔
3. **僅用於個人學習**：不要用於商業盜版或價格監控
4. **尊重數據版權**：亞馬遜內容受版權保護
