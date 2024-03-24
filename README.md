# License
This project is licensed under the [Apache-2.0 license](LICENSE).

# Web Catch
### Web Catch start~ Good news is coming~
实时关注自己在意的网页，并及时提醒，避免错过重要的信息~

# FAQ

### Q: 实现方式?

A: 通过多协程，对多个网页进行请求，检测每个网页某一个 class 标签，对比每次的内容，如果内容有差别时则提醒用户

### Q: 准备环境、运行配置?

A:下载代码后，安装本地环境，凡是 TODO 的地方，及时修改即可，run起来看看吧，大致流程：
 - git clone https://github.com/learnore/WebCatch.git
 - pip install beautifulsoup4
 - 配置邮箱相关信息

### Q: 支持的提醒方式?

A: 
- [x] Email
- [ ] 短信
- [ ] 微信公众号

### Q: 待优化?
A: 
- [ ] 支持 HTML id 元素的检测： div id="content_id"

### Q: 暂不支持名单整理?

A: 
- [ ] B站(要验证)


### Q: 常用命令?

A:
```markdown
1.  rm -rf file_name      # 删除整个文件夹且不用逐一询问
    cd ali_shen/my_workspace/WebCatch
2.  git clone git@github.com:learnore/WebCatch.git
    git stash             # 将未提交的更改保存在一个临时的存储区中
    git pull              # 拉取新代码
    git stash pop         # 恢复暂存的更改
4.  nohup python web_catch_main.py > web_catch_main.log 2>&1 &
    ps aux | grep "web_catch_main.py"
    kill -9 xxxxx
```

# 历史版本

- v1.0 (2024-03-18): 项目迁移到独立仓库、实现邮件提醒
- v1.1 ...
