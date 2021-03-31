function printStatus (requestParams, response, context, ee, next) {
    console.log(`${response.request.uri.path}: ${response.statusCode}`);  
    return next();
}

module.exports = {
    printStatus: printStatus
}
