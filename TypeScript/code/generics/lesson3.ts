type Cover<T> = {
    front: T;
    back: T;
};

const bookCover1: Cover<string> = {
    front: "A Book!",
    back: "author biography",
};

const bookCover2: Cover<number> = {
    front: 15,
    back: 17,
};
