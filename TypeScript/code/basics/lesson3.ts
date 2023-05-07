// arrays
let numbers: number[] = [1,2,3,4,5];
console.log(numbers)

let products: string[] = ["Hats","Shirts","Jeans"];
console.log(products)

let mixData: (string|number)[]=["hi",25,"hello"]
console.log(mixData)

let mixData2: (string|number|boolean)[]=["hi",25,"hello",true]
console.log(mixData2)

let myStrings: string [][]=[["Hi"],["hello","there"]];

let mixDataNested: (string|number)[][] = [
    [1,2,3,4,5,6,7,8,9],
    ["Hi"],
    ["Hello","There"]
]

console.log(mixDataNested);