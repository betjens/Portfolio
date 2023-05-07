let mySet = new Set([1,2,3]);

mySet.add(4);
mySet.has(5);
console.log(mySet.has(5));
console.log(mySet);

let mixedData: Set<string | number> = new Set(["Hi",1]);
//let myArr:(string | number)[] = mixedData;
console.log(mixedData.size);
