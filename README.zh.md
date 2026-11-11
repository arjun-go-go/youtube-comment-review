# 把 YouTube 评论 JSON 整理成审核表

[English](README.md) · [简体中文](README.zh.md)

适合已经拿到评论导出文件、需要把审核工作交给同事的人。脚本把评论与采集状态分开，并把导出文件中能找到的父评论原文放到回复旁边。

只用 Python 标准库。不需要 Apify Token，不请求 YouTube，不启动 Actor，也不会产生新的采集费用。

## 运行

需要 Python 3。解压下载包，在这个目录运行：

```sh
python review_comments.py sample-output.json --out output
```

Windows 也可以用 `py`，macOS / Linux 通常用 `python3`。再次运行会覆盖指定输出目录中的三个同名文件；开始人工标注后，改用一个新的输出目录。

历史样例会生成：

- `comments-review.csv`：40 条评论，含 19 条顶层评论、21 条回复。
- `collection-status.csv`：2 条采集状态，不计入评论数量。
- `export-summary.json`：记录数、去重数、父评论匹配数和原始文件 SHA-256。

在 Excel 或 Google Sheets 中导入 CSV，把 ID 列设为文本，并关闭文本到数字、日期或公式的自动转换。脚本写入 UTF-8 BOM，保留原文内容。`like_count` 和 `collected_at` 是采集时的值，不是实时数据。

## 如何审核

按 `video_id` 和 `parent_comment_id` 找同一条讨论。`parent_comment_text` 是从同一文件匹配到的原文，不是模型生成的摘要；`parent_in_export=false` 表示这份导出没有匹配到父评论，不表示父评论在平台上不存在。顶层评论的这两列留空。

例如，样例中一条回复是 “What do you mean still?”，对应父评论是 “still looks better than my renders”。它是在问另一位观众，不能仅因为带问号就列为产品咨询。

`review_topic`、`next_action`、`owner` 留给审核者填写；`review_status` 初始为 `not_reviewed`。这些是工作列，不是 Actor 的判断。脚本不做情绪分类，不发送回复。

## 使用自己的数据

在 [YouTube Comments Scraper](https://apify.com/arjun_code/youtube-comments-scraper) 完成你需要的运行，下载未筛选字段的 JSON 数组，然后运行：

```sh
python review_comments.py my-comments.json --out my-review
```

需要保留 `recordType`、`videoId`、`commentId`；要关联上下文，还需要 `parentCommentId`、`isReply` 和 `text`。脚本按 `videoId + commentId` 去重，重复时保留文件中第一条，所以不要用它直接合并不同时刻的快照。它将整个文件读入内存，适合小规模人工审核，不是大数据流式处理工具。

重新采集在你的 Apify 账户完成，可能收费。先看当前价格和费用上限。Actor 开发者为 Arjun，链接不是联盟链接。

## 样例来源与核验范围

`sample-output.json` 来自开发项目保存的样例。仓库副本统一使用 LF 换行，JSON 中的值没有改动；`provenance-check.json` 分别记录仓库文件与原始文件的校验值。随附记录将它归于运行 `qln2pjpwCHunRPUKQ`、build `0.1.13`，采集日期为 2026-10-20。`original-input.json` 是该记录保存的输入，包含重复视频链接、无效链接和关闭评论的视频；它不是推荐的首次运行配置。

2026-11-11 复核时，Apify API 与已登录 Console 均未找到这次运行。现阶段可核验的是本地文件一致性、42 条记录的结构，以及从 JSON 到 CSV 的转换，不能重新核验云端运行或保证今天能采到相同评论。不是客户项目、实时结果或效果承诺。详见 `provenance-check.json`。

## 许可

Python 示例代码和原创说明采用 [MIT 许可证](LICENSE)，版权归 Arjun（2026）所有。第三方评论、账号及视频内容不在该许可证范围内，样例数据说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

[完整中文案例](https://madebyarjun.com/zh/youtube-comment-review-guide/?utm_source=github&utm_medium=referral&utm_campaign=comment_review_202611) · [English walkthrough](https://madebyarjun.com/en/youtube-comment-review/?utm_source=github&utm_medium=referral&utm_campaign=comment_review_202611)
