		jw, Sun Mar  4 11:46:34 UTC 2012

This is an enhanced version of osc build

It has the following additional features:
 - builtin debugger. 
   * can jump into a subshell when things go wrong
   * can redo/rewind build steps without any delay.

 - local build with dependencies
   * stores previously built binaries in a reusable location
   * suggests to checkout and build missing dependencies locally.

