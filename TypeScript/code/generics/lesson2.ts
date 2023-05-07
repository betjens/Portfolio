function getArrayItem<T>(item: Array<T>): T {
    return item[2];
}

let number = getArrayItem<number>([1,2,3,4,5])
console.log(number);
