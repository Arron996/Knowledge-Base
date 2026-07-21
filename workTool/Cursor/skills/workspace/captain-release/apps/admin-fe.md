# admin-fe — Captain 发布常量

| 项 | 值 |
|----|-----|
| 仓库 | `/Users/aaron/IdeaProjects/gds-order-admin-fe` |
| application_id | `100059418` |
| GitLab project | `global-rail-gds/gds-order-admin-fe` / `126917` |
| UAT group_id | `81010826` |
| PRO group_id | `91060954` |
| image_url 模板 | `hub.cloud.ctripcorp.com/gitlab-ci/100059418:{tag}` |

## PRO deploy 模板

```json
{
  "group_id": 91060954,
  "image_url": "hub.cloud.ctripcorp.com/gitlab-ci/100059418:REPLACE_TAG",
  "ignore_release_control": true,
  "skip_baking": true,
  "skip_smoking": true,
  "batch": 3,
  "batch_delay": 60,
  "auto_next": 1,
  "note": "REPLACE_NOTE"
}
```

## 常用链接

- 镜像列表：`https://captain.release.ctripcorp.com/app/100059418/image`
- UAT Group：`https://captain.release.ctripcorp.com/app/100059418/group/81010826`
- PRO Group：`https://captain.release.ctripcorp.com/app/100059418/group/91060954`
