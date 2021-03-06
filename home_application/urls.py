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

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'index'),
    (r'^api/test/$', 'test'),
    (r'^search_biz/$', 'search_biz'),
    (r'^search_set/$', 'search_set'),
    (r'^search_host/$', 'search_host'),
    (r'^execute_job/$', 'execute_job'),
    (r'^history/$', 'history'),
    (r'^get_history/$', 'get_history'),
    (r'^fast_execute_script/$', 'fast_execute_script'),
    (r'^get_task_list/$', 'get_task_list'),
    (r'^fast_execute_script_for_task/$', 'fast_execute_script_for_task'),
    # (r'^dev-guide/$', 'dev_guide'),
    # (r'^contactus/$', 'contactus'),
)
