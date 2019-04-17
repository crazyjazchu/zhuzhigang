# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import json
from datetime import datetime, time

from blueking.component.shortcuts import get_client_by_request
from common.log import logger
from common.mymako import render_mako_context, render_json
from home_application.celery_tasks import async_task
from home_application.models import OptHistory


def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def index(request):
    res = search_biz(request);
    return render_mako_context(request, '/home_application/index.html', res)


def search_biz(request):
    myclient = get_client_by_request(request)
    myclient.set_bk_api_ver('v2')
    kwargs = {
        "fields": [
            "bk_biz_id",
            "bk_biz_name"
        ],
    }
    biz_list = []
    myresult = myclient.cc.search_business(kwargs)
    if myresult.get('result'):
        biz_list = myresult.get('data').get('info')
    else:
        logger.info(u"请求业务列表失败：%s" % myresult.get('message'))
        biz_list = []
    return {
        'result': True,
        'data': biz_list
    }


def search_set(request):
    myclient = get_client_by_request(request)
    myclient.set_bk_api_ver('v2')
    biz_id = request.GET.get('biz_id')
    kwargs = {
        "bk_biz_id": int(biz_id),
        "fields": [
            "bk_set_id",
            "bk_set_name"
        ],
    }
    set_list = []
    myresult = myclient.cc.search_set(kwargs)
    if myresult.get('result'):
        set_list = myresult.get('data').get('info')
    else:
        logger.info(u"请求集群列表失败：%s" % myresult.get('message'))
        set_list = []
    return render_json({
        'result': True,
        'data': set_list
    })


def search_host(request):
    myclient = get_client_by_request(request)
    myclient.set_bk_api_ver('v2')
    biz_id = request.GET.get('biz_id')
    set_id = request.GET.get('set_id')
    kwargs = {
        "bk_biz_id": int(biz_id),
        "ip": {
            "data": [],
            "exact": 1,
            "flag": "bk_host_innerip|bk_host_outerip"
        },
        "condition": [
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "module",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "set",
                "fields": [],
                "condition": [
                    {
                        "field": "bk_set_id",
                        "operator": "$eq",
                        "value": int(set_id)
                    }
                ]
            },
            {
                "bk_obj_id": "biz",
                "fields": [
                    "default",
                    "bk_biz_id",
                    "bk_biz_name",
                ],
                "condition": [
                    {
                        "field": "bk_biz_id",
                        "operator": "$eq",
                        "value": int(biz_id)
                    }
                ]
            },
            {
                "bk_obj_id": "object",
                "fields": [],
                "condition": []
            }
        ],
    }
    host_list = []
    myresult = myclient.cc.search_host(kwargs)
    if myresult.get('result'):
        host_list = myresult.get('data').get('info')
    else:
        logger.info(u"请求主机列表失败：%s" % myresult.get('message'))
        host_list = []
    return render_json({
        'result': True,
        'data': host_list
    })


def execute_job(request):
    username = request.user.username
    param = json.loads(request.body)
    biz_id = param.get('biz_id')
    job_id = param.get('job_id')
    ip_list = param.get('ip_list')

    myclient = get_client_by_request(request)
    myclient.set_bk_api_ver('v2')
    # 获取任务详情
    kwargs1 = {
        "bk_biz_id": int(biz_id),
        "bk_job_id": int(job_id)
    }
    data = {}
    myresult = myclient.job.get_job_detail(kwargs1)
    if myresult.get('result'):
        data = myresult.get('data')
    else:
        logger.info(u"请求作业详情失败：%s" % myresult.get('message'))
        data = {}
    logger.info(u"详情：%s" % data)

    steps = data.get('steps')
    steps[0]['ip_list'] = ip_list

    kwargs = {
        "bk_biz_id": int(biz_id),
        "bk_job_id": int(job_id),
        # "global_vars": [
        #     {
        #         "id": 436,
        #         "custom_query_id": [
        #             "3",
        #             "5",
        #             "7"
        #         ],
        #         "ip_list": [
        #             {
        #                 "bk_cloud_id": 0,
        #                 "ip": "10.0.0.1"
        #             },
        #             {
        #                 "bk_cloud_id": 0,
        #                 "ip": "10.0.0.2"
        #             }
        #         ]
        #     },
        #     {
        #         "id": 437,
        #         "value": "new String value"
        #     }
        # ],
        "steps": steps
        #     [{
        #     "script_timeout": 1000,
        #     "script_param": "aGVsbG8=",
        #     "ip_list": [
        #         {
        #             "bk_cloud_id": 0,
        #             "ip": "10.0.0.1"
        #         },
        #         {
        #             "bk_cloud_id": 0,
        #             "ip": "10.0.0.2"
        #         }
        #     ],
        #     "custom_query_id": [
        #         "3"
        #     ],
        #     "script_id": 1,
        #     "script_content": "ZWNobyAkMQ==",
        #     "step_id": 200,
        #     "account": "root",
        #     "script_type": 1
        # },
        #     {
        #         "script_timeout": 1003,
        #         "ip_list": [
        #             {
        #                 "bk_cloud_id": 0,
        #                 "ip": "10.0.0.1"
        #             },
        #             {
        #                 "bk_cloud_id": 0,
        #                 "ip": "10.0.0.2"
        #             }
        #         ],
        #         "custom_query_id": [
        #             "3"
        #         ],
        #         "script_id": 1,
        #         "script_content": "ZWNobyAkMQ==",
        #         "step_id": 1,
        #         "db_account_id": 31
        #     },
        #     {
        #         "file_target_path": "/tmp/[FILESRCIP]/",
        #         "file_source": [
        #             {
        #                 "files": [
        #                     "/tmp/REGEX:[a-z]*.txt"
        #                 ],
        #                 "account": "root",
        #                 "ip_list": [
        #                     {
        #                         "bk_cloud_id": 0,
        #                         "ip": "10.0.0.1"
        #                     },
        #                     {
        #                         "bk_cloud_id": 0,
        #                         "ip": "10.0.0.2"
        #                     }
        #                 ],
        #                 "custom_query_id": [
        #                     "3"
        #                 ]
        #             }
        #         ],
        #         "ip_list": [
        #             {
        #                 "bk_cloud_id": 0,
        #                 "ip": "10.0.0.1"
        #             },
        #             {
        #                 "bk_cloud_id": 0,
        #                 "ip": "10.0.0.2"
        #             }
        #         ],
        #         "custom_query_id": [
        #             "3"
        #         ],
        #         "step_id": 2,
        #         "account": "root"
        #     }]
    }
    job_instance_id = 0
    myresult = myclient.job.execute_job(kwargs)
    if myresult.get('result'):
        job_instance_id = myresult.get('data').get('job_instance_id')
    else:
        logger.info(u"作业实例id失败：%s" % myresult.get('message'))
        job_instance_id = 0
        return render_json({
            'result': False,
            'data': "查询失败"
        })
    # 异步查询记录数据库
    async_task.apply_async(args=(job_instance_id, biz_id, username), kwargs={})
    return render_json({
        'result': True,
        'data': job_instance_id
    })


def history(request):
    res = search_biz(request);
    return render_mako_context(request, '/home_application/history.html', res)


def get_history(request):
    myclient = get_client_by_request(request)
    myclient.set_bk_api_ver('v2')
    biz_id = request.GET.get('biz_id')

    begintime = request.GET.get('begintime')
    endtime = request.GET.get('endtime')

    begin = datetime.fromtimestamp(int(begintime) / 1000)
    end = datetime.fromtimestamp(int(endtime) / 1000)

    historys = OptHistory.objects.filter(bk_biz_id=biz_id).filter(opt_at__gte=begin).filter(opt_at__lte=end). \
        order_by('-opt_at')

    list = []
    for history in historys:
        list.append({"operator": history.operator, "log": history.log, "ip_list": history.ip_list,
                     "bk_biz_name": history.bk_biz_name, "job_status": history.job_status,
                     "opt_at": history.opt_at.strftime("%Y-%m-%d %H:%M:%S"), "job_id": history.job_id})

    return render_json({
        'result': True,
        'data': list
    })


def test(request):
    return render_json({
        'result': True,
        'data': 'hello 程序员，Everything is OK!'
    })
