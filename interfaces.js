_p = process.argv.splice(2)
console.log(require('./encrypt.js').encryptAES(_p[0],_p[1]))
