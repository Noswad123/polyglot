import { hello } from '../exercises/hello'; //polyglot:api

type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends
  (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
type HelloContract = Assert<Equal<typeof hello, () => void>>; //polyglot:api
