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
from django.db import models

# from django.db import models

class OptHistory(models.Model):
    operator = models.CharField(u'操作用户', max_length=128)
    log = models.CharField(u'明细信息', max_length=1000, null=True)
    ip_list = models.GenericIPAddressField(u'IP列表')
    bk_biz_id = models.CharField(u'业务ID', max_length=16)
    bk_biz_name = models.CharField(u'业务名', max_length=16)
    job_status = models.IntegerField(u'任务状态', null=True)
    opt_at = models.DateTimeField(u'操作时间', auto_now_add=True)
    job_id = models.IntegerField(u'任务id', null=True)

    def __unicode__(self):
        return '{}.{}.{}'.format(self.ip_list,
                                 self.job_id,
                                 self.opt_at)

    class Meta:
        verbose_name = '操作记录信息'
        verbose_name_plural = '操作记录信息'

    def toDic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])
