# Movie API Reference - 电影数据库API参考

## TMDB (The Movie Database)

**官网**: https://www.themoviedb.org/
**API文档**: https://developers.themoviedb.org/3/getting-started
**免费层级**: 每日4000次请求

### 基础信息

- Base URL: `https://api.themoviedb.org/3/`
- 图片基础URL: `https://image.tmdb.org/t/p/`
- 支持语言: 多语言（包括中文）
- 认证方式: API Key (bearer token)

### 核心端点

#### 电影搜索
```
GET /search/movie
Parameters:
  - query (required): 搜索关键词
  - language: 语言代码 (zh-CN, en-US)
  - page: 页码
  - include_adult: 是否包含成人内容

Example: /search/movie?query=Inception&language=zh-CN
```

#### 电影详情
```
GET /movie/{movie_id}
Parameters:
  - language: 语言代码

Example: /movie/27205 (Inception)
```

#### 电影credits
```
GET /movie/{movie_id}/credits
Returns: 演员和剧组信息
```

#### 电影图片
```
GET /movie/{movie_id}/images
Returns: 电影海报、剧照等
```

#### 热门电影
```
GET /trending/movie/week
GET /movie/popular
GET /movie/top_rated
GET /movie/now_playing
```

#### 电影类型
```
GET /genre/movie/list
Returns: 所有电影类型列表
```

#### 导演/演员搜索
```
GET /search/person
GET /person/{person_id}
GET /person/{person_id}/movie_credits
```

### 图片尺寸

```
poster_sizes: w92, w154, w185, w342, w500, w780, original
backdrop_sizes: w300, w780, w1280, original
profile_sizes: w45, w185, h632, original
```

## OMDb API

**官网**: http://www.omdbapi.com/
**API Key申请**: http://www.omdbapi.com/apikey.aspx

### 基础信息

- Base URL: `http://www.omdbapi.com/`
- 认证方式: API Key (apikey parameter)
- 免费层级: 每日1000次请求

### 核心端点

#### 电影搜索
```
GET /?apikey=YOUR_KEY&s=MOVIE_TITLE
Parameters:
  - s: 搜索标题
  - type: movie, series, episode
  - y: 年份 (可选)
  - page: 页码
```

#### 电影详情
```
GET /?apikey=YOUR_KEY&i=MOVIE_ID
Parameters:
  - i: IMDb ID
  - plot: short, full
```

### 返回字段

```
Title, Year, Rated, Released, Runtime, Genre,
Director, Writer, Actors, Plot, Language,
Country, Awards, Poster, Ratings, Metascore,
imdbRating, imdbVotes, imdbID, Type, DVD, BoxOffice
```

## 实用查询示例

### 获取电影完整信息
```
1. TMDB搜索电影ID
GET /search/movie?query=卧虎藏龙&language=zh-CN

2. 获取详细信息
GET /movie/{id}?language=zh-CN

3. 获取credits (导演、演员)
GET /movie/{id}/credits?language=zh-CN

4. 获取获奖信息
GET /movie/{id}/release_dates
```

### 获取导演全部作品
```
1. 搜索导演
GET /search/person?query=张艺谋

2. 获取导演电影作品
GET /person/{id}/movie_credits
```

### 获取演员资料
```
1. 搜索演员
GET /search/person?query=梁朝伟

2. 获取演员详情
GET /person/{id}?language=zh-CN

3. 获取演员作品
GET /person/{id}/movie_credits
```

### 电影推荐
```
1. 获取相似电影
GET /movie/{id}/similar

2. 获取推荐电影
GET /movie/{id}/recommendations

3. 获取特定类型
GET /discover/movie?with_genres=28&sort_by=vote_average.desc
```

## 错误处理

### TMDB错误码
```
401: Invalid API key
404: Resource not found
429: Rate limit exceeded
500: Server error
```

### OMDb响应
```
Response: "True" 表示成功
Response: "False" 表示失败
Error: 具体错误信息
```

## 最佳实践

1. **缓存热门数据**: 经典电影信息可以缓存
2. **降级策略**: 主API失败时切换备用
3. **语言适配**: 优先使用中文，未找到时回退英文
4. **分页处理**: 大量结果时分页获取
5. **图片优化**: 根据显示需求选择合适尺寸
