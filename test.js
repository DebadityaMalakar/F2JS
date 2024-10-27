// Generated from FORTRAN source

function doLoop(init, final, step, callback) {
    // Ensure FORTRAN DO loop semantics with at least one iteration
    let index = init;
    if (step > 0 && index <= final) {
        do {
            callback(index);
            index += step;
        } while (index <= final);
    } else if (step < 0 && index >= final) {
        do {
            callback(index);
            index += step;
        } while (index >= final);
    } else if (init === final) {
        // Execute exactly once when init equals final
        callback(init);
    }
}

let x = 0;
x = 10;
console.log('Value of x:', x);
if (( x > 5 )) {
    console.log('x is greater than 5');
}
doLoop(1, 3, 1, (i) => {
    console.log('Loop iteration', i);
});
