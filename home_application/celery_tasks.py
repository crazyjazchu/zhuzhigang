# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import datetime
import json

from celery import task, shared_task
from celery.schedules import crontab
from celery.task import periodic_task

from blueking.component.shortcuts import get_client_by_user
from common.log import logger
from home_application.models import OptHistory


@shared_task()
def async_task(job_instance_id, bk_biz_id, user):
    """
    定义一个 celery 异步任务
    """
    client = get_client_by_user(user)
    get_job_result(job_instance_id, bk_biz_id, client, user)


def get_job_result(task_inst_id, bk_biz_id, client, create_user, max_retries=30, sleep_time=3):
    """
    轮询ijobs任务，返回任务执行的结果，和状态码
    """

    retries = 0
    while retries <= max_retries:
        logger.info(u'【%s】waiting for job finished（%s/%s）' % (task_inst_id, retries, max_retries))
        is_finished, is_ok = get_ijob_result(task_inst_id, bk_biz_id, client, create_user)

        # 等待执行完毕
        if not is_finished:
            retries += 1
            datetime.time.sleep(sleep_time)
            continue

        # 执行成功
        if is_ok:
            logger.info(u'【%s】job execute success' % task_inst_id)
            return True

        # 执行失败
        logger.error(u'执行失败')
        return False

    # 执行超时
    if retries > max_retries:
        return False


def get_ijob_result(task_instance_id, bk_biz_id, client, create_user):
    # 查询作业
    task_info = client.job.get_job_instance_status({'job_instance_id': task_instance_id,
                                                    "bk_biz_id": bk_biz_id
                                                    })
    if task_info.get('code') != 0:
        logger.error(u'error：[%s]' % task_info.get('message'))
        get_job_log(task_instance_id, bk_biz_id, client, create_user)
        return True, False
    else:
        is_ok, is_finished = False, task_info.get('data').get('is_finished')

    if is_finished:
        logger.info(u'【%s】job finished.' % task_instance_id)
        task_instance = task_info.get('data').get('job_instance', {})
        # 作业状态, 2=run, 3=success, 4=fail
        status = task_instance.get('status', 0)
        is_ok = (status == 3)
        get_job_log(task_instance_id, bk_biz_id, client, create_user)
    return is_finished, is_ok


def get_job_log(task_instance_id, bk_biz_id, client, create_user):
    data = client.job.get_job_instance_log({'job_instance_id': task_instance_id,
                                            "bk_biz_id": bk_biz_id
                                            })
    param = {
        "fields": [
            "bk_biz_name"
        ],
        "condition": {
            "bk_biz_id": int(bk_biz_id)
        },
    }
    action_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    biz_result = client.cc.search_business(param)
    if biz_result and biz_result.get('data'):
        biz_name = biz_result.get('data').get('info')[0].get('bk_biz_name')
        status = data.get('data')[0].get('status')
        results = data.get('data')[0].get('step_results')
        ip_list = []
        log_list = []
        for result in results:
            for ip_content in result.get("ip_logs"):
                ip = ip_content.get("ip")
                log = ip_content.get('log_content')
                log = ip + "|" + log
                ip_list.append(ip)
                log_list.append(log)
            OptHistory.objects.create(
                operator=create_user,
                log=json.dumps(log_list),
                ip_list=json.dumps(ip_list),
                bk_biz_id=bk_biz_id,
                bk_biz_name=biz_name,
                job_status=status,
                opt_at=action_time,
                job_id=int(task_instance_id)
            )
    else:
        OptHistory.objects.create(
            operator=create_user,
            log=json.dumps([]),
            ip_list=json.dumps([]),
            bk_biz_id=bk_biz_id,
            bk_biz_name="",
            job_status=4,
            opt_at=action_time,
            job_id=int(task_instance_id)
        )


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    now = datetime.datetime.now()
    logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # 调用定时任务
    async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))


@periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))
