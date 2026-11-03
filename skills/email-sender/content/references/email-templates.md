# 邮件模板参考

## 1. 欢迎邮件

```
主题：欢迎加入 {platform_name}！

正文：
亲爱的 {username}，

欢迎来到 {platform_name}！

我们很高兴您加入我们的社区。以下是一些入门提示：

1. 完成个人资料设置
2. 探索主要功能
3. 如需帮助，查看我们的帮助中心

开始您的旅程 →
{promo_link}

祝好，
{company_name} 团队
```

## 2. 密码重置邮件

```
主题：[安全] 密码重置请求

正文：
您好 {username}，

我们收到了您的密码重置请求。如果您没有请求此操作，请忽略此邮件。

重置密码链接（24小时内有效）：
{reset_link}

此链接只能使用一次。

安全提示：
• 请勿将密码告知任何人
• 确保设备安全

如果您有任何疑问，请联系我们的支持团队。

祝好，
{company_name} 安全团队
```

## 3. 订单确认邮件

```
主题：订单 #{order_id} 确认

正文：
尊敬的 {username}，

感谢您的订单！

订单详情：
- 订单号：{order_id}
- 订单日期：{order_date}
- 总金额：{total_amount}

配送地址：
{shipping_address}

预计送达时间：{estimated_delivery}

查看订单详情 →
{order_link}

感谢您的购买！

祝好，
{company_name} 客户服务团队
```

## 4. 促销邮件

```
主题：🔥 {promo_title} | 仅限 {end_date}

正文：
亲爱的 {username}，

{promo_description}

✨ 优惠详情：
{discount_details}

⏰ 优惠截止：{end_date}

{CTA_BUTTON}

优惠码：{promo_code}

条款与条件：
{terms_conditions}

---
退订邮件：{unsubscribe_link}
```

## 5. 新闻通讯邮件

```
主题：{newsletter_title} - {date}

正文：
您好 {username}，

📰 本期内容：

1. {article_1_title}
   {article_1_summary}
   阅读更多 → {article_1_link}

2. {article_2_title}
   {article_2_summary}
   阅读更多 → {article_2_link}

3. {article_3_title}
   {article_3_summary}
   阅读更多 → {article_3_link}

---
{cta_section}

---
退订邮件：{unsubscribe_link}
© {year} {company_name}. All rights reserved.
{company_address}
```

## 6. 会议邀请邮件

```
主题：会议邀请：{meeting_title}

正文：
尊敬的 {recipient_name}，

您收到一封会议邀请。

📅 会议详情：
- 会议主题：{meeting_title}
- 时间：{meeting_date_time}
- 时长：{duration}
- 会议链接：{meeting_link}

议程：
{agenda}

参会人员：
{attendees_list}

请确认是否参加 →
{rsvp_link}

祝好，
{sender_name}
{company_name}
```

## HTML 邮件设计规范

### 响应式设计
```html
<!-- 最大宽度 600px，适合邮件客户端 -->
<table width="600" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td>
      <!-- 内容 -->
    </td>
  </tr>
</table>
```

### 按钮样式
```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center">
      <a href="{cta_link}"
         style="background-color: #007bff;
                color: #ffffff;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;">
        {button_text}
      </a>
    </td>
  </tr>
</table>
```

### 颜色对比度
- 确保文字与背景对比度符合 WCAG 2.1 标准
- 文字颜色：#333333 或更深的颜色
- 背景颜色：#FFFFFF 或浅色

### 字体推荐
- 正文：16px Arial, Helvetica
- 标题：24-32px Georgia, serif
- 按钮文字：14-16px Arial, sans-serif
