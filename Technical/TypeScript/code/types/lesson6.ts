type Employee = {
    id: number,
    name: string,
    department: string,
};

const employee: Employee = {
    id: 1,
    name: "scott",
    department: "design",
};

const hiredEmployee = JSON.stringify(employee);
console.log(typeof hiredEmployee)

function getEmployeeInfo(employeeObject:string) {
    //return JSON.parse(employeeObject);
    return (<Employee>JSON.parse(employeeObject)); 
}

console.log(getEmployeeInfo(hiredEmployee))