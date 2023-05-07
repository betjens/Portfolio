let tip = (billAmount: number, tipPercentage: string | number): number => {
    if (typeof tipPercentage === "number") {
        return billAmount * tipPercentage
    } else {
        let calculateTip: number = billAmount * (parseInt(tipPercentage))
        return calculateTip;
    }
};

//let tipAmount=tip(100,0.15);
let tipAmount=tip(100,"20");
console.log(tipAmount);