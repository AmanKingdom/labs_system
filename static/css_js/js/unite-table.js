//动态合并单元格
function uniteTable(tableId) {//表格ID，表格列数
    var tb=document.getElementById(tableId);
    tb.style.display='';
    var i = 0;
    var j = 0;
    rowCount = tb.rows.length; //   行数
    colCount = tb.rows[0].cells.length; //   列数

    console.log('行列数:', rowCount, colCount);

    var obj1 = null;
    var obj2 = null;
    //为每个单元格命名，包括表头
    for (i = 0; i < rowCount; i++) {
        for (j = 0; j < colCount; j++) {
            tb.rows[i].cells[j].id = "tb__" + i.toString() + "_" + j.toString();
            // console.log(tb.rows[i].cells[j], tb.rows[i].cells[j].id);
        }
    }

    //合并列，在本程序，应该先做行方向上的合并，因为课程往往是有多个实验室，而在一周的一串节次内，基本都是合并后的一整个大单元格
    for (i = 1; i < rowCount; i++) {    // i作为行标
        // 不能这样用：obj1 = document.getElementById(tb.rows[i].cells[2].id);
        obj1 = document.getElementById("tb__"+i.toString()+"_2");   // 从每一行的第3列开始取单元格对象元素，因为星期和节次不需要做列合并
        // console.log('合并列，目前行和obj1：', i, obj1);

        for (j = 3; j < colCount; j++) {    // 从第4列开始取每一行的单元格作为下一个判断对象
            if(document.getElementById("tb__"+i.toString()+"_"+j.toString())){
                // console.log('存在obj2：',document.getElementById("tb__"+i.toString()+"_"+j.toString()));

                // console.log('现在的obj1和obj2分别为：', obj1, obj2, '处于第', i, '行，第', j, '列');

                obj2 = document.getElementById("tb__"+i.toString()+"_"+j.toString());
                if (obj1.innerText === obj2.innerText && (obj2.innerText !== "")) {
                    obj1.colSpan++;
                    // console.log('删除第', i, '行，第', j, '列的元素');
                    obj2.parentNode.removeChild(obj2);
                } else {
                    obj1 = obj2;
                }
            }else{
                // console.log('不存在第', i, '行，第', j, '列的元素');
            }
        }
    }

    //合并行
    for (i = 0; i < colCount; i++) {    // i作为列标
        if(i !== 1) {   // i==1时，是节次那一列，这列不用合并

            // 由于前面已经处理了列的合并，有一些列的开头是没有单元格了的，所以要经过一轮当前列的循环找到第一个非空的单元格
            var k = 1;  // 从第二行开始，也就是表体开始，因为第一行是表头
            for(k; k < rowCount; k++){
                if(document.getElementById("tb__"+ k.toString()+ "_" + i.toString())) {
                    obj1 = document.getElementById("tb__"+ k.toString()+ "_" + i.toString());
                    break;
                }
            }
            if(obj1){
                for (j=k+1; j < rowCount; j++) {    // 这里的j是用来取obj2的，所以要+1
                    if (document.getElementById("tb__" + j.toString() + "_" + i.toString())) {
                        obj2 = document.getElementById("tb__" + j.toString() + "_" + i.toString());

                        // console.log('现在的obj1和obj2分别为：', obj1, obj2, '处于第', j, '行，第', i, '列');

                        if (obj1.innerText === obj2.innerText && (obj2.innerText !== "")) {
                            if(obj1.getAttribute("colspan") === obj2.getAttribute("colspan")) {
                                // console.log('obj1和obj2的跨列数：', obj1.colspan,obj2.colspan);
                                obj1.rowSpan++;
                                // console.log('删除第', j, '行，第', i, '列的元素');
                                obj2.parentNode.removeChild(obj2);
                            }
                        } else {
                            obj1 = document.getElementById("tb__" + j.toString() + "_" + i.toString());
                        }
                    } else {
                        // console.log('不存在第', j, '行，第', i, '列的元素');
                    }
                }
            }
        }
    }
}
