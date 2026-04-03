let holidaySalesX = (
    product: string,
    sales: number,
    tax: number,
    discount: number
): number => {
    let price: number = 0;

    if (product == "sunglasses") price = 29;
    if (product == "hats") price = 19;
    if (product == "shoes") price = 59;

    let totalSalesforIndividualProduct: number = price * sales;

    return (totalSalesforIndividualProduct -
        tax * totalSalesforIndividualProduct -
        discount * totalSalesforIndividualProduct);
};

const shoes: number = holidaySalesX("shoes", 50, 0.25, 0.15);

console.log(`The total profit from the sales of shoes is ${shoes}.`);