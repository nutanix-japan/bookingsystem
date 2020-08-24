let CANVAS_MONTH_FONT = '18px "M PLUS 1p"'
let CANVAS_DATE_FONT = '14px "M PLUS 1p"'
let CANVAS_ASSET_FONT = '18px "M PLUS 1p"'
let CANVAS_BOOKING_FONT = '16px "M PLUS 1p"'

let COLOR_BLACK = 'rgb(15,30,40)'
let COLOR_WHITE = 'rgb(255,255,255)'
let COLOR_ORANGE = 'rgba(247,159,31, 0.85)'
let COLOR_RED = 'rgb(235,47,6)'
let COLOR_PINK = 'rgba(253,167,223, 0.5)'

/*
each page
*/
let loaded = false
let today = new Date()
let year = today.getYear() + 1900
let month = today.getMonth() + 1
let eventListnerAdded = false
let json = []

let page_index = function(){
  // get asset list and booking status
  $.getJSON('/api/v1/booking/', function(jsonbody){
    json = jsonbody
    loaded = true
    drawCanvas(year, month, json)
  })
  .fail(function(data){
    console.log(data)
  })
}

let clearCanvas = function(){
  let canvas = document.getElementById('canvas')
  let context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
}

let click_thismonth = function(){
  if(!loaded){
    return
  }
  today = new Date()
  year = today.getYear() + 1900
  month = today.getMonth() + 1
  console.log(json)

  clearCanvas()
  drawCanvas(year, month, json)
}

let click_prev = function(){
  if(!loaded){
    return
  }
  if(month == 1){
    year -= 1
    month = 12
  }else{
    month -= 1
  }
  console.log(json)

  clearCanvas()
  drawCanvas(year, month, json)
}

let click_next = function(){
  if(!loaded){
    return
  }
  if(month == 12){
    year += 1
    month = 1
  }else{
    month += 1
  }
  console.log(json)

  clearCanvas()
  drawCanvas(year, month, json)
}

let page_create = function(){
  let dateFormat = 'yy-mm-dd';
  $('.dateinput').datepicker({dateFormat: dateFormat});
}



/*
draw gant chart
*/

let global_year = -1
let global_month = -1

let functionMap = []


let initFunctionMap = function(){
  let canvas = document.getElementById('canvas')
  //console.log(canvas.width)
  //console.log(canvas.height)
  functionMap = []
  for(let x=0; x<=canvas.width; x++){
    functionMap.push([])
    for(let y=0; y<=canvas.height; y++){
      functionMap[x].push(false)
    }
  }
}

let addEventListener = function(){
  if(eventListnerAdded){
    return
  }
  eventListnerAdded = true
  
  function onClick(e){
    let rect = e.target.getBoundingClientRect();
    let x = Math.floor(e.clientX - rect.left)
    let y = Math.floor(e.clientY - rect.top)
    fun = functionMap[x][y]
    if(fun){
      // on booking area
      fun()
    }
  }

  function onMouseMove(e){
    let rect = e.target.getBoundingClientRect();
    let x = Math.floor(e.clientX - rect.left)
    let y = Math.floor(e.clientY - rect.top)
    if(functionMap[x][y]){
      document.body.style.cursor = 'pointer';
    }else{
      document.body.style.cursor = 'default';
    }
  }

  let canvas = document.getElementById('canvas')
  canvas.addEventListener('click', onClick, false);
  canvas.addEventListener('mousemove', onMouseMove, false);
}

let registerFunction = function(x, y, width, height, fun){
  for(let i=x; i<=x+width; i++){
    for(let j=y; j<=y+height; j++){
      functionMap[i][j] = fun
    }
  }
}

let drawCanvas = function(year, month, assets){
  function getStartEndDate(year, month, fromDate, toDate){
    month -= 1
    let day1UnixTime = new Date(year, month, 1).getTime()
    let dayLastUnixTime = new Date(year, month + 1 , 0).getTime()
    let fromArray = fromDate.split('-')
    let fromUnixTime = new Date(Number(fromArray[0]), Number(fromArray[1] -1), Number(fromArray[2])).getTime()
    let toArray = toDate.split('-')
    let toUnixTime = new Date(Number(toArray[0]), Number(toArray[1] -1), Number(toArray[2])).getTime()     

    if(toUnixTime < day1UnixTime){
      return [false, 0, 0]
    }
    if(dayLastUnixTime < fromUnixTime){
      return [false, 0, 0]
    }

    let startUnixTime = 0
    if(fromUnixTime < day1UnixTime){
      startUnixTime = day1UnixTime
    }else{
      startUnixTime = fromUnixTime
    }

    let endUnixTime = 0
    if(dayLastUnixTime < toUnixTime){
      endUnixTime = dayLastUnixTime
    }else{
      endUnixTime = toUnixTime
    }

    let startDate = (new Date(startUnixTime)).getDate()
    let endDate = (new Date(endUnixTime)).getDate()  
    console.log(new Date(endUnixTime))
    return [true, startDate, endDate]
  }

  function getBookingText(context, startDate, endDate, userName, groupName, purpose){
    let width = 30 * (endDate - startDate + 1) - 10
    let lastText = ''
    let text = ''
    let textWidth = 0
    
    text = userName
    textWidth = context.measureText(text).width
    if(width < textWidth){
      // longest chars of userName
      for(let i=userName.length; 0<i; i--){
        text = userName.substr(0, i)
        textWidth = context.measureText(text).width
        if(textWidth < width){
          return text
        }
      }
      return ''
    }else{
      lastText = text
    }

    text = userName + ' (' + groupName + ')'
    textWidth = context.measureText(text).width
    if(width < textWidth){
      return lastText
    }else{
      if(purpose == ''){
        return text
      }
      lastText = text
    }    

    text = userName + ' (' + groupName + ') : ' + purpose
    textWidth = context.measureText(text).width
    if(width < textWidth){
      return lastText
    }

    return text

    /*
    let days = endDate - startDate
    if(days <= 1){
      return ''
    }else if(days <= 2){
      return userName.substr(0, 4)
    }else if(days <= 5){
      return userName
    }else if(days <= 8){
      return userName + ' (' + groupName + ')'
    }else{
      return userName + ' (' + groupName + ') : ' + purpose
    }
    */
  }

  let canvas = document.getElementById('canvas')
  canvas.height = 110 + 40 * assets.length

  let context = document.getElementById('canvas').getContext('2d');
  drawMonth(context, year, month, assets.length)
  initFunctionMap()
  addEventListener()

  for(let row=0; row<assets.length; row++){
    let asset = assets[row]

    // text color
    let color = COLOR_BLACK
    expDateStr = asset['assetExpirationDate']
    if(expDateStr !== null){
      let expDateArray = expDateStr.split('-')
      let expDateUnixTime = new Date(Number(expDateArray[0]), Number(expDateArray[1] -1), Number(expDateArray[2])).getTime()
      let today = new Date()
      let todayUnixTime = new Date(today.getYear() + 1900, today.getMonth(), today.getDate()).getTime()
      let diffDays = (expDateUnixTime - todayUnixTime) / (1000 * 60 * 60 * 24)
      if(diffDays < 60){
        color = COLOR_RED
      }
    }
    
    let fun = function(){
      $('#assetmodal-name').text(asset['assetName'])
      $('#assetmodal-model').text(asset['assetModelNumber'])
      $('#assetmodal-serial').text(asset['assetSerialNumber'])
      $('#assetmodal-install').text(asset['assetInstallationDate'])
      $('#assetmodal-expiration').text(asset['assetExpirationDate'])
      $('#assetmodal-active').text(asset['active'] + '')
      $('#assetmodal-note').text(asset['assetNote'])

      expDateStr = asset['assetExpirationDate']
      if(expDateStr !== null){
        let expDateArray = expDateStr.split('-')
        let expDateUnixTime = new Date(Number(expDateArray[0]), Number(expDateArray[1] -1), Number(expDateArray[2])).getTime()
        let today = new Date()
        let todayUnixTime = new Date(today.getYear() + 1900, today.getMonth(), today.getDate()).getTime()
        let diffDays = (expDateUnixTime - todayUnixTime) / (1000 * 60 * 60 * 24)
        if(diffDays < 60){
          $('#assetmodal-expiration').addClass('red')
          $('#assetmodal-expiration2').addClass('red')
        }else{
          $('#assetmodal-expiration').removeClass('red')
          $('#assetmodal-expiration2').removeClass('red')
        }
      }else{
        $('#assetmodal-expiration').removeClass('red')
        $('#assetmodal-expiration2').removeClass('red')
      }

      let assetUpdateUrl = '/asset/' + asset['assetId'] + '/update'
      $('#assetmodal-edit').attr('onclick', "location.href='" + assetUpdateUrl + "'")

      document.body.style.cursor = 'default';
      $('#assetModal').modal('show');
    }
    drawAsset(context, row, asset, color, fun)

    let bookings = asset['bookings']
    for(let column=0; column<bookings.length; column++){
      let booking = bookings[column]
      let result = getStartEndDate(year, month, booking['fromDate'], booking['toDate'])
      if(!result[0]){
        // not in this month. skip drawing.
        continue
      }

      let startDate = result[1]
      let endDate = result[2]
      
      let backgroundColor = booking['backgroundColor']
      let text = getBookingText(context, startDate, endDate, booking['ownerUserName'], 
        booking['ownerGroupName'], booking['purpose'])

      let textWidth = context.measureText(text).width
      console.log('textWidth:' + textWidth)

      let textColor = booking['textColor']
      let fun = function(){
        //console.log($('#bookingmodal-asset'))
        $('#bookingmodal-asset').text(asset['assetName'])
        $('#bookingmodal-user').text(booking['ownerUserName'])
        $('#bookingmodal-group').text(booking['ownerGroupName'])
        $('#bookingmodal-purpose').text(booking['purpose'])
        $('#bookingmodal-fromdate').text(booking['fromDate'])
        $('#bookingmodal-shippingdate').text(booking['shippingDate'])
        $('#bookingmodal-returndate').text(booking['returnDate'])
        $('#bookingmodal-todate').text(booking['toDate'])
        $('#bookingmodal-note').text(booking['note'])

        let today = new Date()
        let todayUnixTime = new Date(today.getYear() + 1900, today.getMonth(), today.getDate()).getTime()
        let toArray = booking['toDate'].split('-')
        let toUnixTime = new Date(Number(toArray[0]), Number(toArray[1] -1), Number(toArray[2])).getTime()

        if(todayUnixTime > toUnixTime){
          $('#bookingmodal-update').addClass('disabled')
          $('#bookingmodal-update').attr('onclick', '')
        }else{
          $('#bookingmodal-update').removeClass('disabled')
          bookingUpdateUrl = '/booking/' + booking['bookingId'] + '/update'
          $('#bookingmodal-update').attr('onclick', "location.href='" + bookingUpdateUrl + "'")
        }

        if(todayUnixTime >= toUnixTime){
          $('#bookingmodal-release').addClass('disabled')
          $('#bookingmodal-release').attr('onclick', '')
        }else{
          $('#bookingmodal-release').removeClass('disabled')
          bookingReleaseUrl = '/booking/' + booking['bookingId'] + '/release'
          $('#bookingmodal-release').attr('onclick', "location.href='" + bookingReleaseUrl + "'")
        }

        document.body.style.cursor = 'default';
        $('#bookingModal').modal('show');
      }
      drawBooking(context, row, startDate, endDate, backgroundColor, text, textColor, fun)
    }
  }
}

let showBookingModal = function(){
  document.body.style.cursor = 'default';
  $('#bookingModal').modal('show');
}

let drawMonth = function(context, year, month, num_assets){
  month -= 1
  context.fillStyle = COLOR_BLACK
  context.font = CANVAS_MONTH_FONT

  // show month
  let mL = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
   'September', 'October', 'November', 'December'];
  let MonthText = mL[month] + ' ' + year
  context.fillText(MonthText, 130, 30)

  // show date
  let today = new Date()
  let checkDate = (today.getYear() + 1900) == year && today.getMonth() == month
  let endDate  = new Date(year, month + 1 , 0).getDate();
  let rectHeight = 40 + 40 * num_assets
  context.font = CANVAS_DATE_FONT
  for(let date=1; date<=endDate; date++){
    let x = 100 + 30 * date

    if(checkDate && today.getDate() == date){
      // background
      context.fillStyle = COLOR_ORANGE
      context.fillRect(x, 50, 30, rectHeight)
      // date number
      context.fillStyle = COLOR_WHITE
      let strDate = ('00' + date).slice(-2)
      context.fillText(strDate, x + 6, 70)

    }else{
      // background
      let day = new Date(year, month, date).getDay()
      if(day == 0 || day == 6){
        // sunday or saturday
        context.fillStyle = COLOR_PINK
        context.fillRect(x, 50, 30, rectHeight)
        // date number
        context.fillStyle = COLOR_BLACK
        let strDate = ('00' + date).slice(-2)
        context.fillText(strDate, x + 6, 70)
      }else{
        // date number
        context.fillStyle = COLOR_BLACK
        let strDate = ('00' + date).slice(-2)
        context.fillText(strDate, x + 6, 70)
      }
    }
  }
}

let drawAsset = function(context, row, asset, color, fun){
  let y = 110 + 40 * row
  registerFunction(10, y - 25, 90, 30, fun)

  context.fillStyle = color
  context.font = CANVAS_ASSET_FONT
  context.textAlign = 'left'
  context.fillText(asset['assetName'], 20, y, 100)
}

let drawBooking = function(context, row, fromDate, toDate, color, text, textColor, fun){
  let x = 100 + 30 * fromDate
  let y = 90 + 40 * row
  let width = 30 * (toDate - fromDate + 1)
  let height = 30
  let radius = 6

  // rectangle
  registerFunction(x, y, width, height, fun)
  function drawRect(param) {
    var ctx = param.ctx;
    var x = param.x + 1; // make small white space on left
    var y =param.y;
    var width = param.width - 2; // make small white space on right
    var height = param.height;
    var radius = param.radius || 0;
    var color = param.color;
    
    ctx.save();
      ctx.fillStyle = color;
      ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.arc(x + width - radius, y + radius, radius, Math.PI * 1.5, 0, false);
        ctx.lineTo(x + width, y + height - radius);
        ctx.arc(x + width - radius, y + height - radius, radius, 0, Math.PI * 0.5, false);
        ctx.lineTo(x + radius, y + height);
        ctx.arc(x + radius, y + height - radius, radius, Math.PI * 0.5, Math.PI, false);
        ctx.lineTo(x, y + radius);
        ctx.arc(x + radius, y + radius, radius, Math.PI, Math.PI * 1.5, false);
      ctx.closePath();
      ctx.fill();
    ctx.restore();
  }
  drawRect({
    ctx : context,
    x : x,
    y : y,
    width: width,
    height: height,
    radius: radius,
    color: color
  });

  // text
  let tx = x + width/2
  let ty = y + 20
  let twidth = width - 5
  context.font = CANVAS_BOOKING_FONT
  context.fillStyle = textColor
  context.textAlign = 'center'
  context.fillText(text, tx, ty, twidth)
}