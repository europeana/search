/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
PR.registerLangHandler(PR.createSimpleLexer([["pln",/^[\t\n\r \xa0\u2028\u2029]+/,null,"\t\n\r �\xa0  "],["str",/^(?:["\u201c\u201d](?:[^"\u201c\u201d]|["\u201c\u201d]{2})(?:["\u201c\u201d]c|$)|["\u201c\u201d](?:[^"\u201c\u201d]|["\u201c\u201d]{2})*(?:["\u201c\u201d]|$))/i,null,'"“”'],["com",/^['\u2018\u2019].*/,null,"'‘’"]],[["kwd",/^(?:addhandler|addressof|alias|and|andalso|ansi|as|assembly|auto|boolean|byref|byte|byval|call|case|catch|cbool|cbyte|cchar|cdate|cdbl|cdec|char|cint|class|clng|cobj|const|cshort|csng|cstr|ctype|date|decimal|declare|default|delegate|dim|directcast|do|double|each|else|elseif|end|endif|enum|erase|error|event|exit|finally|for|friend|function|get|gettype|gosub|goto|handles|if|implements|imports|in|inherits|integer|interface|is|let|lib|like|long|loop|me|mod|module|mustinherit|mustoverride|mybase|myclass|namespace|new|next|not|notinheritable|notoverridable|object|on|option|optional|or|orelse|overloads|overridable|overrides|paramarray|preserve|private|property|protected|public|raiseevent|readonly|redim|removehandler|resume|return|select|set|shadows|shared|short|single|static|step|stop|string|structure|sub|synclock|then|throw|to|try|typeof|unicode|until|variant|wend|when|while|with|withevents|writeonly|xor|endif|gosub|let|variant|wend)\b/i,
null],["com",/^rem.*/i],["lit",/^(?:true\b|false\b|nothing\b|\d+(?:e[+-]?\d+[dfr]?|[dfilrs])?|(?:&h[\da-f]+|&o[0-7]+)[ils]?|\d*\.\d+(?:e[+-]?\d+)?[dfr]?|#\s+(?:\d+[/-]\d+[/-]\d+(?:\s+\d+:\d+(?::\d+)?(\s*(?:am|pm))?)?|\d+:\d+(?::\d+)?(\s*(?:am|pm))?)\s+#)/i],["pln",/^(?:(?:[a-z]|_\w)\w*|\[(?:[a-z]|_\w)\w*])/i],["pun",/^[^\w\t\n\r "'[\]\xa0\u2018\u2019\u201c\u201d\u2028\u2029]+/],["pun",/^(?:\[|])/]]),["vb","vbs"]);
