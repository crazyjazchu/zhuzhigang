onchangeBiz()
function onchangeBiz(params) {
    var biz_id = $('#selectBiz').val();
    $.ajax({
        type: "get",
        url: site_url + "search_set/",
        data: {
            'biz_id': biz_id
        },
        dataType: "json",
        success: function (response) {
            console.log(response)
            str = ''
            for (let index = 0; index < response.data.length; index++) {
                const element = response.data[index];
                bk_set_id = element.bk_set_id
                bk_set_name = element.bk_set_name
                str += `<option value="${bk_set_id}">${bk_set_name}</option>`
            }
            $('#selectSet').html(str);
            onchangeSet()
        }
    });
};

function onchangeSet(params) {
    var biz_id = $('#selectBiz').val()
    var set_id = $('#selectSet').val()
    $.ajax({
        type: "get",
        url: site_url + "search_host/",
        data: {
            'biz_id': biz_id,
            'set_id': set_id
        },
        dataType: "json",
        success: function (response) {

            console.log(response)
            str = ''
            for (let index = 0; index < response.data.length; index++) {
                const element = response.data[index];
                str += `<tr data-ip="${element.host.bk_host_innerip}" data-bk_cloud_id="${element.host.bk_cloud_id[0].bk_inst_id}">
                    <td>${element.host.bk_host_innerip}</td>
                    <td>${element.host.bk_os_name}</td>
                    <td>${element.host.bk_host_name}</td>
                    <td>${element.host.bk_cloud_id[0].bk_inst_name}</td>
                    <td>${element.host.bk_cloud_id[0].bk_inst_id}</td>
                </tr>
                `
            }
            $('#tbody-ip').html(str)
        }
    });
}

function runJob(params) {
    // 执行任务
    var biz_id = $('#selectBiz').val()
    var ip_list = []
    var tabtr = $('#tbody-ip tr')
    console.log(tabtr)
    $(tabtr).each(function (indexInArray, valueOfElement) {
        ip_list.push({
            'ip': $(this).attr('data-ip'),
            'bk_cloud_id': $(this).attr('data-bk_cloud_id')
        })
    });


    param = {
        'biz_id': biz_id,
        'job_id': 50,
        'ip_list': ip_list
    }
    $.ajax({
        type: "post",
        url: site_url + "execute_job/",
        data: JSON.stringify(param),
        dataType: "json",
        headers: {
            "Content-Type": "application/json;charset=utf-8"
        },
        success: function (response) {
            console.log(response)
            alert("执行成功")

        }
    });
}

function myquery(params) {
    var times = $('#daterangepicker_demo3').val()
    var time1 = times.split(' 至 ')
    var begintime = new Date(time1[0]).getTime()
    var endtime = new Date(time1[1]).getTime()
    var biz_id = $('#selectBiz').val()
    console.log(times)
    $.ajax({
        type: "get",
        url: site_url + "get_history/",
        data: {
            'biz_id': biz_id,
            'begintime': begintime,
            'endtime': endtime
        },
        dataType: "json",
        success: function (response) {
            console.log(response)
            str = ''
            for (let index = 0; index < response.data.length; index++) {
                const element = response.data[index];
                str += `<tr>
                    <td>${element.operator}</td>
                    <td>${element.log}</td>
                    <td>${element.ip_list}</td>
                    <td>${element.bk_biz_name}</td>
                    <td>${element.job_status}</td>
                    <td>${element.opt_at}</td>
                    <td>${element.job_id}</td>
                </tr>
                `
            }
            $('#tbody-ip').html(str)

        }
    });
}

onchange4myhosts()
function onchange4myhosts(params) {
    var biz_id = $('#selectBiz').val()
    var set_id
    $.ajax({
        type: "get",
        url: site_url + "search_host/",
        data: {
            'biz_id': biz_id,
            'set_id': set_id
        },
        dataType: "json",
        success: function (response) {

            console.log(response)
            str = ''
            for (let index = 0; index < response.data.length; index++) {
                const element = response.data[index];
                str += `<tr data-ip="${element.host.bk_host_innerip}" data-bk_cloud_id="${element.host.bk_cloud_id[0].bk_inst_id}">
                    <td><input type="checkbox" value=""></td>
                    <td>${index}</td>
                    <td>${element.host.bk_host_innerip}</td>
                    <td>${element.host.bk_os_name}</td>
                </tr>
                `
            }
            $('#tbody-ip1').html(str)
        }
    });
};

function clickbb(params) {
    // 业务id
    var biz_id = $('#selectBiz').val()
    var task_id = $('#task_type_list').val()
    var records = $('#table_demo2>tbody input:checked').closest('tr');

    if (!records.length) {
        alert('请选择执行的ip记录！');
        return false;
    }
    // 选中ip列表
    var ip_list = []
    $(records).each(function (indexInArray, valueOfElement) {
        ip_list.push({
            'ip': $(this).attr('data-ip'),
            'bk_cloud_id': $(this).attr('data-bk_cloud_id')
        })
    });

    param = {
        'biz_id': biz_id,
        'task_id': task_id,
        'ip_list': ip_list
    }
    $.ajax({
        type: "post",
        url: site_url + "fast_execute_script_for_task/",
        data: JSON.stringify(param),
        dataType: "json",
        success: function (response) {
            console.log(response)
        }
    });


};