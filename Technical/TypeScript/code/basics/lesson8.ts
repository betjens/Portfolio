let mixDataFor: (string|number)[]=["Cosmos",13,50,"Star"];

// for (let item of mixData) 

for (let item of mixDataFor.entries()) console.log(item[0],item[1]);

let data: (string|number)[] =["Cosmos",13,50,"Star"];

for (let datapoint in data){
    //console.log(typeof datapoint);
    console.log(`${+datapoint+1}-${data[datapoint]}`);
}
