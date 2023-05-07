//Enum

const enum RollNumbers {
    John = 1,
    Kelly,
    Sandra,
    Joseph,
    Samantha,
}
let studentRollNumber1: RollNumbers = RollNumbers.Sandra
let studentRollNumber2: RollNumbers = RollNumbers.Samantha

console.log(studentRollNumber1);
console.log(studentRollNumber2);

// string Enum Types
const enum StudentDetails{
    Name="John",
    Major="Arts",
}

let studentName: StudentDetails = StudentDetails.Name
let studentMajor: StudentDetails = StudentDetails.Major

console.log(studentName,studentMajor)

// Hetergeneous Enums

const enum MixStudentDetails{
    ID=1,
    Name="John",
    Major="Arts",
}

let MixstudentName: MixStudentDetails = MixStudentDetails.Name
let MixstudentMajor: MixStudentDetails = MixStudentDetails.Major
let MixstudentId: MixStudentDetails = MixStudentDetails.ID
console.log(`${MixstudentId} - ${MixstudentName} has a major in ${MixstudentMajor}`)