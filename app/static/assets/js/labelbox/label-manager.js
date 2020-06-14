// 定义全局变量
var pOrder = 0;
var pBtnStatus = 0;

$(function() {
    /*初始化拖拽功能*/
    // dragged_init();  // 点击标签后在函数那边初始化

    /* input输入框扩展(回车提交，监听input值) */
    $("input.search").bind("input propertychange", function () {
    // 监听输入内容，如果有内容就显示后面的×
        if ($(this).val() != "") {
            $("a.search-reset").fadeIn();
        } else {
            $("a.search-reset").fadeOut();
        }
    });
    // 点击×消除内容
    $("a.search-reset").click(function () {
        $(this).siblings(".search").val("");
        $(this).fadeOut();
    });
    // 判断是不是回车
    $("input.search").keypress(function (e) {
        // 兼容写法
        e = e || window.event;
        key = e.keyCode || e.which || e.charCode;
        if (key == 13) {
            // 根据输入框内容动态插入数据
            var leadHtml='';     
            var bmName = 'myinsert';
            var bcolor= $(this).parent().css('border-color');
            
            var color_id = $(this).parent().attr("id"); // 测试根据id获取颜色
            // console.log(color_id);
  
            pOrder += 1;
            leadHtml+='<li id="'+bmName+pOrder+'-'+color_id+'" data-bs="'+'lead'+'">' +
                '<span class="badge"'+'style="background:'+bcolor+';color:#fff;">'+$("input.search").val()+'</span>' +
                '</li>'
            $("#owner-wrapper-add").append(leadHtml);
            
            // 初始化拖拽功能
            dragged_init();

            // 完事后清空内容
            $("a.search-reset").siblings(".search").val("");
            $("a.search-reset").fadeOut();

            // 修改模态框高度
            change_modal_height();
        }
    });


    /* 点击修改输入框和自定义标签的颜色 */
    $("button.change-color").click(function () {
        // 截取id对应的color
        var color_id = $(this).attr("id").split('-')[1];
        // 针对按下的不同按钮，修改search-box的id属性为对应颜色
        $(".search-box").attr("id",color_id);
        switch(color_id)
        {
            case "red":
                console.log("change red color");
                $(".search-box").css("border", "2px solid #ee2558");
                break;
            case "green":
                console.log("change green color");
                $(".search-box").css("border", "2px solid #04BE5B");
                break;
            case "blue":
                console.log("change blue color");
                $(".search-box").css("border", "2px solid #46b6fe");
                break;
            case "amber":
                console.log("change amber color");
                $(".search-box").css("border", "2px solid #f9bd65");
                break;
            case "purple":
                console.log("change purple color");
                $(".search-box").css("border", "2px solid #673AB7");
                break;
            case "pink":
                console.log("change pink color");
                $(".search-box").css("border", "2px solid #ff4dab");
                break;
            case "cyan":
                console.log("change cyan lime");
                $(".search-box").css("border", "2px solid #5CC5CD");
                break;
            case "yellow":
                console.log("change red yellow");
                $(".search-box").css("border", "2px solid #fdd932");
                break;
        }
    });      

    /* 模态框关闭按钮（隐藏）的触发函数：关闭不做任何反应（不保存） */
    $('#LabelManagerModal').on('hide.bs.modal',
        // 隐藏模态框触发函数
        function() {
        // showSuccessMessage();
    });

    // 打开模态框后自动修改高度
    $('#LabelManagerModal').on('shown.bs.modal', function () {
        // $('#myInput').focus()
        change_modal_height();
    });

});


function dragged_init(){
    // 对待选区的无序列表的每一个<li>，设定属性
    // 开放还原位置功能
    $(".list-wrapper li").draggable({
        revert: true
    });

    /*拖拽追加事件*/
    // top-droppable指定已选择区的待拖入框
    // 待选区的每一个<li>都有指定拖拽目标到特定的data-bs
    $(".top-droppable").topDroppable({
        drop: function (e, ui) {
            var parentNode=$(this).parents(".form-content");
            var parentNextNode=$(this).parents(".selected-box").next().find(".people-list");
            var jScore=Number($(this).next("div").find(".numSpan").text());
            var totalScore=Number($(this).next("div").find(".totalNum").text());
            // 判断有没有超出区域(form-content和head描述的div就是界限)
            if($(ui.draggable[0]).attr("data-bs")==parentNode.attr("data-bs")){
                // 判断是否超出数量限制
                if($(this).next(".score-xz").hasClass("num-xz")){
                    if((jScore)<totalScore){
                        $(this).next("div").find(".numSpan").html(jScore+1)
                    }else{   
                        alert("超出可选人数上限");                 
                        return
                    }
                }else{
                    $(this).next("div").find(".numSpan").html(jScore+1)
                }
                $(this).parents(".form-content").height("auto");
                $(this).parents(".selected-box").next().find(".people-list").height("auto");
                // 添加到框里
                var sourceElement = $(ui.draggable);
                console.log(sourceElement.attr("id"));
                var sourceColor = change_dragged_color(sourceElement.attr("id"));
//                console.log('看看attr(id)',this,$(ui.draggable[0]).attr('id'));
                $(this).append('<div class="'+$(ui.draggable[0]).attr('id')+'" style="margin:0px;">'+'<span class="badge" style="background:'+sourceColor+
                    ';color:#fff;">'+$(ui.draggable[0]).text()+'</span>'+'<span class="del"></span></div>');
                $(ui.draggable[0]).hide();      
                // 修改模态框高度
                change_modal_height();          
            }else{
                alert("不可越界");
            }
        }
    }).droppable({
        tolerance: "pointer"
    });

    /* 已选标签框，删除事件会在待选框复原 */
    $(".score-wrapper").on("click",".del",function(){
        var parentNode=$(this).parents(".form-content");
        var parentNextNode=$(this).parents(".selected-box").next().find(".people-list");
        var jScore=Number($(this).parents(".score-wrapper").find(".score-xz").find(".numSpan").text());
        var totalScore=Number($(this).parents(".score-wrapper").find(".score-xz").find(".totalNum").text());
        $("#"+$(this).parent().attr("class")).show();
        if(jScore>0){
            $(this).parents(".score-wrapper").find(".score-xz").find(".numSpan").html(jScore-1)
        }
        $(this).parent().remove();
        if(parentNextNode.height()>parentNode.height()){
            parentNode.height(parentNextNode.height());
        }
        // 修改模态框高度
        change_modal_height();
    });
}


function change_modal_height(){
    // 经过测试 body≈box1+box2+box3-120
    var box1 = $(".selected-box").height();
    var box2 = $("#basic-check-box").height();
    var box3 = $("#custom-check-box").height();
    var body = box1+box2+box3-120;
    // console.log("change height:",body,box1,box2,box3);
    $("#label-modal-body").height(body);
}

function change_dragged_color(sourceId)
{
    // 截取id对应的color
    var color_id = sourceId.split('-')[1];
    // 针对不同的color_id做响应
    switch(color_id)
    {
        case "red":
            return "#ee2558";
        case "green":
            return "#04BE5B";
        case "blue":
            return "#46b6fe";
        case "amber":
            return "#f9bd65";
        case "purple":
            return "#673AB7";
        case "pink":
            return "#ff4dab";
        case "cyan":
            return "#5CC5CD";
        case "yellow":
            return "#fdd932";
    }
}

<!-- 加载每个用户对应的基础标签和自定义标签 -->
function showUserLabels(num, basic_label_relations, custom_label_relations, basic_label_roles, custom_label_roles, username){
    var leadHtml = '';
    var tmp,sourceId,sourceColor;
    var choice_view_num = 0;
    var choice_limit_num = 0;
    var basic_choice_label = basic_label_relations['choice'][num];
    var basic_free_label = basic_label_relations['free'][num];
    var basic_choice_view = basic_label_relations['view'][num];
    var basic_choice_limit = basic_label_relations['limit'][num];

    var custom_choice_label = custom_label_relations['choice'][num];
    var custom_free_label = custom_label_relations['free'][num];
    var custom_choice_view = custom_label_relations['view'][num];
    var custom_choice_limit = custom_label_relations['limit'][num];

    // 修改标签弹窗所属的用户名
    $("#label-box-name").text(username);

    // 清空原有模态框
    $("#li-basic-content").html("");
    $("#li-custom-content").html("");
    $("#choice-view").html("");
    $("#choice-limit").html("");
    // 保存按键状态以便在其他地方调用
    pBtnStatus = num;
    // ------------------------------------ 基础标签相关 ------------------------------------ //
    // 显示基础待选框-全部数据
    for (var i = 0; i < basic_label_roles['name'].length; i++) {
        leadHtml = '<li id="basic'+i+'-'+basic_label_roles['color'][i]+'" data-bs="lead">'+
            '<span title="'+basic_label_roles['remarks'][i]+'" class="badge badge-'+
            basic_label_roles['color'][i]+'">'+basic_label_roles['name'][i]+'</span></li>';
        $("#li-basic-content").append(leadHtml);
    }
    // 显示基础待选框-隐藏已选数据 && 显示已选框的基础标签
    for (var i = 0; i < basic_choice_label.length; i++) {
        sourceId = 'basic'+basic_choice_label[i]+'-'+basic_label_roles['color'][basic_choice_label[i]];
        sourceColor = change_dragged_color(sourceId);
        leadHtml = '<div class="'+sourceId+'" style="margin:0px;">'+'<span class="badge" style="background:'+sourceColor+
            ';color:#fff;">'+$('#'+sourceId).text()+'</span>'+'<span class="del"></span></div>';
        $('#'+sourceId).hide();
        // 判断是属于view还是属于limit
        if(basic_choice_view[i] == 1){
            $(".top-droppable#choice-view").append(leadHtml);
            choice_view_num += 1;
        }
        if(basic_choice_limit[i] == 1){
            $(".top-droppable#choice-limit").append(leadHtml);
            choice_limit_num += 1;
        }
    }
    // ------------------------------------ 自定义标签相关 ------------------------------------ //
    // 显示自定义待选框-全部数据
    for (var i = 0; i < custom_label_roles['name'].length; i++) {
        leadHtml = '<li id="custom'+i+'-'+custom_label_roles['color'][i]+'" data-bs="lead">'+
            '<span title="'+custom_label_roles['remarks'][i]+'" class="badge badge-'+
            custom_label_roles['color'][i]+'">'+custom_label_roles['name'][i]+'</span></li>';
        $("#li-custom-content").append(leadHtml);
    }
    // 显示自定义待选框-隐藏已选数据 && 显示已选框的基础标签
    for (var i = 0; i < custom_choice_label.length; i++) {
        sourceId = 'custom'+custom_choice_label[i]+'-'+custom_label_roles['color'][custom_choice_label[i]];
        sourceColor = change_dragged_color(sourceId);
        leadHtml = '<div class="'+sourceId+'" style="margin:0px;">'+'<span class="badge" style="background:'+sourceColor+
            ';color:#fff;">'+$('#'+sourceId).text()+'</span>'+'<span class="del"></span></div>';
        $('#'+sourceId).hide();
        // 判断是属于view还是属于limit
        if(custom_choice_view[i] == 1){
            $(".top-droppable#choice-view").append(leadHtml);
            choice_view_num += 1;
        }
        if(custom_choice_limit[i] == 1){
            $(".top-droppable#choice-limit").append(leadHtml);
            choice_limit_num += 1;
        }
    }

    // 修改已选框的最小数值
    $("#choice-view-num").text(choice_view_num);
    $("#choice-limit-num").text(choice_limit_num); //???/
    // 初始化拖拽功能(点击后初始化，保证整个模态框只有这里最先，增加效率)
    dragged_init();
    // 修改模态框高度
    // change_modal_height(); // 不需要重复修改
}

// ------------- 标签弹窗确认按钮触发：保存已选框的标签数据并传到后端 ------------- //
//function showSuccessMessage() {
//    var sourceId, sourceField, sourceIndex, sourceColor, tmp;
//    var basic_view_done = [];
//    var basic_limit_done = [];
//    var custom_view_done = [];
//    var custom_limit_done = [];
//    var insert_view_done = [];
//    var insert_limit_done = [];
//    // 遍历choice-view框内的所有div
//    $('#choice-view div').each(function(i){
//        sourceId = $(this).attr("class");
//        tmp = sourceId.split("-")[0];
//        sourceColor = sourceId.split("-")[1];
//        sourceField = tmp.substring(0, tmp.length-1);
//        sourceIndex = tmp.substring(tmp.length-1, tmp.length);
//        if(sourceField == 'basic')
//            basic_view_done.push(sourceIndex);
//        if(sourceField == 'custom' || sourceField == 'myinsert')
//            custom_view_done.push(sourceIndex);
//        if(sourceField == 'myinsert')
//            insert_view_done.push({'index':sourceIndex,'color':sourceColor});
//    });
//    // 遍历choice-limit框内的所有div
//    $('#choice-limit div').each(function(i){
//        sourceId = $(this).attr("class");
//        tmp = sourceId.split("-")[0];
//        sourceColor = sourceId.split("-")[1];
//        sourceField = tmp.substring(0, tmp.length-1);
//        sourceIndex = tmp.substring(tmp.length-1, tmp.length);
////        console.log($(this).attr("class"), sourceField, sourceIndex);
//        if(sourceField == 'basic')
//            basic_limit_done.push(sourceIndex);
//        if(sourceField == 'custom')
//            custom_limit_done.push(sourceIndex);
//        if(sourceField == 'myinsert')
//            insert_limit_done.push({'index':sourceIndex,'color':sourceColor});
//    });
//    console.log('view_done:',basic_view_done,custom_view_done,insert_view_done);
//    console.log('limit_done:',basic_limit_done,custom_limit_done,insert_limit_done);
//
//    swal({
//            text: "已生效",
//            icon: "success",
//            button: {
//                visible: false,
//            },
//            timer: 1500,
//    });
//}