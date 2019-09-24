  /*
  *     System Mappings
  * */

  var AutoOps = (function(){

      function AutoOps(){
          var props = {
              card : {
                  index : ['应用发布','中间件部署','参数变更','账号管理','车险平台','农险平台','健康险平台','保单登记'],
                  img : [149, 139, 119, 155, 88, 87, 89, 90],
                  color : ['0097dc','6a4fd0','ecca42','e05fc2','ff9966','613884','317dad','236e6b'],
                }
          };
          var timeTool = {
              /*
               *   时间戳格式化为时间字符串
               * */
              formatTimestamp : function(inputTime, form){
                  var date = new Date(inputTime * 1000);
                  var dateContainer = []
                  var y = date.getFullYear();
                  y = form.indexOf('yyyy') != -1 ? y : y.toString().slice(2);
                  var M = date.getMonth() + 1;
                  M = (M < 10) & (form.indexOf('MM') != -1) ? ('0' + M) : M;
                  var d = date.getDate();
                  d = (d < 10) & (form.indexOf('dd') != -1) ? ('0' + d) : d;
                  var h = date.getHours();
                  h = (h < 10) & (form.indexOf('hh') != -1) ? ('0' + h) : h;
                  var m = date.getMinutes();
                  m = (m < 10) & (form.indexOf('mm') != -1) ? ('0' + m) : m;
                  var s = date.getSeconds();
                  s = (s < 10) & (form.indexOf('ss') != -1) ? ('0' + s) : s;
                  form = form.replace('yyyy',y)
                      .replace('yy',y)
                      .replace('MM',M)
                      .replace('M',M)
                      .replace('dd',d)
                      .replace('d',d)
                      .replace('hh',h)
                      .replace('h',h)
                      .replace('mm',m)
                      .replace('m',m)
                      .replace('ss',s)
                      .replace('s',s);
                  return form;
              },
              /*
               *   计算两个时间戳的时间差
               * */
              calTimestampDiff : function(earlyTime, laterTime){
                  var earlyDate = new Date(earlyTime * 1000);
                  var laterDate = new Date(laterTime * 1000);
                  var timeDiff=laterDate.getTime()-earlyDate.getTime();  //时间差的毫秒数
                  //计算出相差天数
                  var days=Math.floor(timeDiff/(24*3600*1000))
                  //计算出小时数
                  var leave1=timeDiff%(24*3600*1000)    //计算天数后剩余的毫秒数
                  var hours=Math.floor(leave1/(3600*1000))
                  //计算相差分钟数
                  var leave2=leave1%(3600*1000)        //计算小时数后剩余的毫秒数
                  var minutes=Math.floor(leave2/(60*1000))
                  //计算相差秒数
                  var leave3=leave2%(60*1000)      //计算分钟数后剩余的毫秒数
                  var seconds=Math.round(leave3/1000)
                  var timediffdict = {
                      'days' : days,
                      'hours' : hours,
                      'minutes' : minutes,
                      'seconds' : seconds
                  };
                  return timediffdict;
              },
              formatTimeStr : function(timeStr){
                  return (new Date(timeStr.replace(/-/g,'/')).getTime()) / 1000;
              },
              checkTimeLgNowTime : function(timestamp){
                  return timestamp > (Math.round(new Date() / 1000))
              },
              checkStartLgEnd : function(start, end){
                  return start > end
              }
          };
          var valueTool = {
              formatJSONArray : function(jsonarray){
                  var values = {};
                  $.each(jsonarray, function(index, item){
                      values[item.name] = item.value;
                  });
                  return values;
              }
          };
          this.getMapping = function(name, prop, key){
              return props[name][prop][props[name]['index'].indexOf(key)];
          };
          this.getTimeTool = function(toolname){
              return timeTool[toolname]
          };
          this.getValueTool = function(toolname){
              return valueTool[toolname];
          };
          this.getTemp = function(tempName){
              return temp[tempName]
          };
          this.getCheckTool = function(ctName){
              return checkData[ctName]
          };
          this.toggleValue = function(currectValue, valueList){
              var index = valueList.indexOf(currectValue);
              var nextIndex = index + 1;
              if(nextIndex >= valueList.length){
                  nextIndex = 0;
              }
              return valueList[nextIndex];
          }

      }
      var autoops;
      var _static = {
        name: 'AutoOps',
            getInstance: function () {
                if (autoops === undefined) {
                    autoops = new AutoOps();
                }
                return autoops;
            }
        };
        return _static;

  })();

  autoops = AutoOps.getInstance();

  function cronValidate() {
        var cron = $("#cron").val();
        var result = CronExpressionValidator.validateCronExpression(cron);
        if(result == true){
            alert("格式正确");
        }
        else{
            alert("格式错误");
        }
        return CronExpressionValidator.validateCronExpression(cron);
    }
    function CronExpressionValidator() {
    }

    CronExpressionValidator.validateCronExpression = function(value) {
        var results = true;
        if (value == null || value.length == 0) {
            return false;
        }

        // split and test length
        var expressionArray = value.split(" ");
        var len = expressionArray.length;

        if ((len != 6) && (len != 7)) {
            return false;
        }

        // check only one question mark
        var match = value.match(/\?/g);
        if (match != null && match.length > 1) {
            return false;
        }

        // check only one question mark
        var dayOfTheMonthWildcard = "";

        // if appropriate length test parts
        // [0] Seconds 0-59 , - * /
        if (CronExpressionValidator.isNotWildCard(expressionArray[0], /[\*]/gi)) {
            if (!CronExpressionValidator.segmentValidator("([0-9\\\\,-\\/])", expressionArray[0], [0, 59], "seconds")) {
                return false;
            }
        }

        // [1] Minutes 0-59 , - * /
        if (CronExpressionValidator.isNotWildCard(expressionArray[1], /[\*]/gi)) {
            if (!CronExpressionValidator.segmentValidator("([0-9\\\\,-\\/])", expressionArray[1], [0, 59], "minutes")) {
                return false;
            }
        }

        // [2] Hours 0-23 , - * /
        if (CronExpressionValidator.isNotWildCard(expressionArray[2], /[\*]/gi)) {
            if (!CronExpressionValidator.segmentValidator("([0-9\\\\,-\\/])", expressionArray[2], [0, 23], "hours")) {
                return false;
            }
        }

        // [3] Day of month 1-31 , - * ? / L W C
        if (CronExpressionValidator.isNotWildCard(expressionArray[3], /[\*\?]/gi)) {
            if (!CronExpressionValidator.segmentValidator("([0-9LWC\\\\,-\\/])", expressionArray[3], [1, 31], "days of the month")) {
                return false;
            }
        } else {
            dayOfTheMonthWildcard = expressionArray[3];
        }

        // [4] Month 1-12 or JAN-DEC , - * /
        if (CronExpressionValidator.isNotWildCard(expressionArray[4], /[\*]/gi)) {
            expressionArray[4] = CronExpressionValidator.convertMonthsToInteger(expressionArray[4]);
            if (!CronExpressionValidator.segmentValidator("([0-9\\\\,-\\/])", expressionArray[4], [1, 12], "months")) {
                return false;
            }
        }

        // [5] Day of week 1-7 or SUN-SAT , - * ? / L C #
        if (CronExpressionValidator.isNotWildCard(expressionArray[5], /[\*\?]/gi)) {
            expressionArray[5] = CronExpressionValidator.convertDaysToInteger(expressionArray[5]);
            if (!CronExpressionValidator.segmentValidator("([0-9LC#\\\\,-\\/])", expressionArray[5], [1, 7], "days of the week")) {
                return false;
            }
        } else {
            if (dayOfTheMonthWildcard == String(expressionArray[5])) {
                return false;
            }
        }

        // [6] Year empty or 1970-2099 , - * /
        if (len == 7) {
            if (CronExpressionValidator.isNotWildCard(expressionArray[6], /[\*]/gi)) {
                if (!CronExpressionValidator.segmentValidator("([0-9\\\\,-\\/])", expressionArray[6], [1970, 2099], "years")) {
                    return false;
                }
            }
        }
        return true;
    };

    // ----------------------------------
    // isNotWildcard 静态方法;
    // ----------------------------------
    CronExpressionValidator.isNotWildCard = function(value, expression) {
        var match = value.match(expression);
        return (match == null || match.length == 0) ? true : false;
    };

    // ----------------------------------
    // convertDaysToInteger 静态方法;
    // ----------------------------------
    CronExpressionValidator.convertDaysToInteger = function(value) {
        var v = value;
        v = v.replace(/SUN/gi, "1");
        v = v.replace(/MON/gi, "2");
        v = v.replace(/TUE/gi, "3");
        v = v.replace(/WED/gi, "4");
        v = v.replace(/THU/gi, "5");
        v = v.replace(/FRI/gi, "6");
        v = v.replace(/SAT/gi, "7");
        return v;
    }

    // ----------------------------------
    // convertMonthsToInteger 静态方法;
    // ----------------------------------
    CronExpressionValidator.convertMonthsToInteger = function(value) {
        var v = value;
        v = v.replace(/JAN/gi, "1");
        v = v.replace(/FEB/gi, "2");
        v = v.replace(/MAR/gi, "3");
        v = v.replace(/APR/gi, "4");
        v = v.replace(/MAY/gi, "5");
        v = v.replace(/JUN/gi, "6");
        v = v.replace(/JUL/gi, "7");
        v = v.replace(/AUG/gi, "8");
        v = v.replace(/SEP/gi, "9");
        v = v.replace(/OCT/gi, "10");
        v = v.replace(/NOV/gi, "11");
        v = v.replace(/DEC/gi, "12");
        return v;
    };

    // ----------------------------------
    // segmentValidator 静态方法;
    // ----------------------------------
    CronExpressionValidator.segmentValidator = function(expression, value, range, segmentName) {
        var v = value;
        var numbers = new Array();

        // first, check for any improper segments
        var reg = new RegExp(expression, "gi");
        if (!reg.test(v)) {
            return false;
        }

        // check duplicate types
        // check only one L
        var dupMatch = value.match(/L/gi);
        if (dupMatch != null && dupMatch.length > 1) {
            return false;
        }

        // look through the segments
        // break up segments on ','
        // check for special cases L,W,C,/,#,-
        var split = v.split(",");
        var i = -1;
        var l = split.length;
        var match;

        while (++i < l) {
            // set vars
            var checkSegment = split[i];
            var n;
            var pattern = /(\w*)/;
            match = pattern.exec(checkSegment);

            // if just number
            pattern = /(\w*)\-?\d+(\w*)/;
            match = pattern.exec(checkSegment);

            if (match
                    && match[0] == checkSegment
                    && checkSegment.indexOf("L") == -1
                    && checkSegment.indexOf("l") == -1
                    && checkSegment.indexOf("C") == -1
                    && checkSegment.indexOf("c") == -1
                    && checkSegment.indexOf("W") == -1
                    && checkSegment.indexOf("w") == -1
                    && checkSegment.indexOf("/") == -1
                    && (checkSegment.indexOf("-") == -1 || checkSegment
                            .indexOf("-") == 0) && checkSegment.indexOf("#") == -1) {
                n = match[0];

                if (n && !(isNaN(n)))
                    numbers.push(n);
                else if (match[0] == "0")
                    numbers.push(n);
                continue;
            }
    // includes L, C, or w
            pattern = /(\w*)L|C|W(\w*)/i;
            match = pattern.exec(checkSegment);

            if (match
                    && match[0] != ""
                    && (checkSegment.indexOf("L") > -1
                            || checkSegment.indexOf("l") > -1
                            || checkSegment.indexOf("C") > -1
                            || checkSegment.indexOf("c") > -1
                            || checkSegment.indexOf("W") > -1 || checkSegment
                            .indexOf("w") > -1)) {

                // check just l or L
                if (checkSegment == "L" || checkSegment == "l")
                    continue;
                pattern = /(\w*)\d+(l|c|w)?(\w*)/i;
                match = pattern.exec(checkSegment);

                // if something before or after
                if (!match || match[0] != checkSegment) {
                    continue;
                }

                // get the number
                var numCheck = match[0];
                numCheck = numCheck.replace(/(l|c|w)/ig, "");

                n = Number(numCheck);

                if (n && !(isNaN(n)))
                    numbers.push(n);
                else if (match[0] == "0")
                    numbers.push(n);
                continue;
            }

            var numberSplit;

            // includes /
            if (checkSegment.indexOf("/") > -1) {
                // take first #
                numberSplit = checkSegment.split("/");

                if (numberSplit.length != 2) {
                    continue;
                } else {
                    n = numberSplit[0];

                    if (n && !(isNaN(n)))
                        numbers.push(n);
                    else if (numberSplit[0] == "0")
                        numbers.push(n);
                    continue;
                }
            }

            // includes #
            if (checkSegment.indexOf("#") > -1) {
                // take first #
                numberSplit = checkSegment.split("#");

                if (numberSplit.length != 2) {
                    continue;
                } else {
                    n = numberSplit[0];

                    if (n && !(isNaN(n)))
                        numbers.push(n);
                    else if (numberSplit[0] == "0")
                        numbers.push(n);
                    continue;
                }
            }

    // includes -
            if (checkSegment.indexOf("-") > 0) {
                // take both #
                numberSplit = checkSegment.split("-");

                if (numberSplit.length != 2) {
                    continue;
                } else if (Number(numberSplit[0]) > Number(numberSplit[1])) {
                    continue;
                } else {
                    n = numberSplit[0];

                    if (n && !(isNaN(n)))
                        numbers.push(n);
                    else if (numberSplit[0] == "0")
                        numbers.push(n);
                    n = numberSplit[1];

                    if (n && !(isNaN(n)))
                        numbers.push(n);
                    else if (numberSplit[1] == "0")
                        numbers.push(n);
                    continue;
                }
            }

        }
        // lastly, check that all the found numbers are in range
        i = -1;
        l = numbers.length;

        if (l === 0)
            return false;

        while (++i < l) {
            // alert(numbers[i]);
            if (numbers[i] < range[0] || numbers[i] > range[1]) {
                return false;
            }
        }
        return true;
    };


    /*
    *   检测对象
    * */

    var Check = function(){
        this.init();
    };
    Check.prototype.init = function(){};

    // 检测数组中是否包含空值
    Check.prototype.check_listEmpty = function(check_list){
        var hasEmpty = false;
        $.each(check_list, function (index, item) {
            if (item === "" || item === undefined){
                hasEmpty = true;
            }
        });
        return hasEmpty;
    };

    // 检测表单列表中的空值
    Check.prototype.check_formEmpty = function(form_list){
        var hasEmpty = false;
        $.each(JSON.parse(form_list), function (index, item) {
            if (item.value === ""){
                hasEmpty = true;
            }
        });
        return hasEmpty;
    };

    /*
    *   工具对象
    * */

    var Tool = function(){
        this.prosecutor = null;
        this.init();
    };
    Tool.prototype.init = function(){
        this.prosecutor = new Check();
    };

    window.apstool = new Tool();
    window.None = "";


