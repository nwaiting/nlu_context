> 此工程作为小语料情况下的预处理模块，上下文继承模块的一种方法。
>
>       优点：易于维护，扩展方便；
>           一个人一个月的开发工期，优化工期你不定；
>           可以支撑万级日活。
>       此为工程代码，主要本人完成，存在诸多不足，欢迎提出问题，互相学习，一起维护。

> 1.nlu模块，目前包含 预处理， 结合上下文复写模块。
>
> 2.日志目录：     /export/longzai/project_normal/nlu_log
>
> 3.启动文件路径：
>
>       /export/app/bot_factory_nlu/nlu_dir/online/nlu_api.py
>
>&emsp;&emsp;启动命令：
>
>        nohup python nlu_api.py 9047 2>/nlu_api.log 1>nlu_api.log &
>
>&emsp;&emsp;端口：xxx
>
> 4.测试
>
>    文件路径：
>
>         tests/test_api_inter.py  用于控制台实时输入，观察输出结果
>         tests/test_api_nlu.py   测试文件，如果没有报错，说明api接口正常正常
>
>    测试方式： python test_api_inter.py

- 词典路径
    /export/app/bot_factory_nlu/nlu_dir/data/userdict/entity

- 子文件：
>       company_domain.txt
        entity_intent.txt
        company_property.txt
        entity_domain.txt
        entity_property.txt
