(this.webpackJsonpbrokadminpanel=this.webpackJsonpbrokadminpanel||[]).push([[0],{21:function(e,t){e.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAADUElEQVR4nO2cTUsbQRjHn2qE1Lz4QtGTEYyIBxVLjwq1xWuhH6F67zcomILfoPf2U+TcWiziqaVW9KChKoLQLRrdxLC7xjJhDbszY/7JZlYoPD/Yw87OS/zhPPvsZiYUMwUiuo3xWIz7D+hRShgW1AksCJBofbkjBojoabDBs2x2PJPofAi3XqcL11XKZf667vyZ4wQHKBPRd6ViF5gUNEtEn4MFr0ZGaC2fVyoi/jgOfbUsUIvoXan04cxxgkXfTAdunmIAFgRgQYBuYtAqEeXuTuYzmbHXo6OhCs+Hh5VGJnk5NERz6XSzx8rNzVjRsgrSEF/8IxLdClq4O0knEpECcjcIQUH2q9Vc0bLWNF1GFsRTDMCCACwI8Kj15Sar/tHk48zM7FQqlb07z/T20lwmozSUebu3Rz+urpTyICKTLnteqEzEGznmyFzX63RUq4VKt8rl46Jlncgfo92Mu90gnQsGZMFUKkULg4NKRcQv26bN83NQSyV4t7qPxz09NN3fH7r607Zzwbutz8A9XSjwFAOwIIBuig34D55NRBKYlp7KRcxBHNdqdCLFBPf2doeILkFTBZEEijwnWD6eTDamVSue9PXRdCoVqnHhujNnjuNJzTZ13eiC9JL8VF6YnIyUBL4/PKTCwYFc/CJi4iYy5FASuJ7PKzGnHdZKJdqtVOSaOhc8xRAsCMCCALogHQkRkD+dnoaa7tq2iDUbUn+/Iw6hxK2tcnnFz3MaiICMkslOMSZI3K00AXnDD64mUF5bFC1rOZgEiruVaUE8xQAsCMCCACwIwIIALAjAggAsCMCCACwIwIIALAhgcn2QjnH/DWVcZGPsu0Hcgt74x38LTzEACwKwIICxGDSWTDa+HjJBxfPo6Pq6457EK1fTGBOUSyaNLaBqd5XrQ8BTDMCCACwIwIIALAjAggAsCGAsD7r0PNqxbaU8CmIr1H612nFLsZhKLKoyiTFBQs7i9rZS/pCI7+bXJyaMjshTDMCCACwIEPcbRd0CKpOsaBaJGyVuQSYXUOlYjlsQTzEACwKwIAALArAgAAsCsCAAC4rAksFfjIozSSR/j5du3CiHFv4PArAgAAsC6B5WL3RbjyISdetTu4i97/inqpiYIKJ/H/T/fbHJO4kAAAAASUVORK5CYII="},30:function(e,t,a){e.exports=a(47)},35:function(e,t,a){},42:function(e,t,a){},45:function(e,t,a){},47:function(e,t,a){"use strict";a.r(t);var n=a(0),r=a.n(n),c=a(25),o=a.n(c),s=(a(35),a(8)),l=a(13),u=a(29),i=a(2),m=a.n(i),h=a(4),d=a(15),p=a(16),f="http://localhost:5000/api/v1/";var E=new(function(){function e(){Object(d.a)(this,e)}return Object(p.a)(e,[{key:"isAuthenticated",value:function(){return!!localStorage.getItem("email")}},{key:"getAuthToken",value:function(){var e=localStorage.getItem("email"),t=window.atob(localStorage.getItem("password")),a="".concat(e,":").concat(t);return this.createAuthToken(a)}},{key:"createAuthToken",value:function(e){return window.btoa(e)}},{key:"login",value:function(){var e=Object(h.a)(m.a.mark((function e(t){var a,n,r,c,o,s;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return a=t.email,n=t.password,r="".concat(a,":").concat(n),c=this.createAuthToken(r),e.prev=3,e.next=6,fetch(f+"user",{method:"GET",headers:{Authorization:"Basic ".concat(c)}});case 6:return o=e.sent,e.next=9,o.json();case 9:if(s=e.sent,o.ok){e.next=12;break}throw new Error(s.msg);case 12:"admin"!==s.type&&"moderator"!==s.type||(localStorage.setItem("role",s.type),localStorage.setItem("email",s.email),localStorage.setItem("password",window.btoa(n))),e.next=18;break;case 15:throw e.prev=15,e.t0=e.catch(3),e.t0;case 18:case"end":return e.stop()}}),e,this,[[3,15]])})));return function(t){return e.apply(this,arguments)}}()},{key:"logout",value:function(){var e=Object(h.a)(m.a.mark((function e(){return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:localStorage.clear();case 1:case"end":return e.stop()}}),e)})));return function(){return e.apply(this,arguments)}}()}]),e}());function b(e){var t=e.children,a=Object(u.a)(e,["children"]);return r.a.createElement(l.b,Object.assign({},a,{render:function(e){var a=e.location;return E.isAuthenticated()?t:r.a.createElement(l.a,{to:{pathname:"/login",state:{from:a}}})}}))}function v(e){return r.a.createElement(l.a,{to:"/dashboard"})}var g=a(6),w=a(49),A=a(51),k=a(52),x=a(50);a(42);function j(e){var t=Object(n.useState)(""),a=Object(g.a)(t,2),c=a[0],o=a[1],s=Object(n.useState)(""),u=Object(g.a)(s,2),i=u[0],d=u[1],p=Object(l.g)();if(E.isAuthenticated())return r.a.createElement(l.a,{to:"/dashboard"});function f(){return(f=Object(h.a)(m.a.mark((function e(t){return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t.preventDefault(),e.prev=1,e.next=4,E.login({email:c,password:i});case 4:p.push("/dashboard/lots/unapproved"),e.next=10;break;case 7:e.prev=7,e.t0=e.catch(1),console.error(e.t0);case 10:case"end":return e.stop()}}),e,null,[[1,7]])})))).apply(this,arguments)}return r.a.createElement("div",{className:"Login"},r.a.createElement("h1",{className:"login_heading"},"Login"),r.a.createElement("form",{onSubmit:function(e){return f.apply(this,arguments)}},r.a.createElement(w.a,{controlId:"email"},r.a.createElement(A.a,null,"Email"),r.a.createElement(k.a,{autoFocus:!0,type:"text",value:c,onChange:function(e){return o(e.target.value)}})),r.a.createElement(w.a,{controlId:"password"},r.a.createElement(A.a,null,"Password"),r.a.createElement(k.a,{value:i,onChange:function(e){return d(e.target.value)},type:"password"})),r.a.createElement(x.a,{className:"login-btn",block:!0,disabled:!(c.length>0&&i.length>7),type:"submit"},"Login")))}function y(e){return{cash:"\u041d\u0430\u043b\u0438\u0447\u043d\u044b\u0435",cashless:"\u0411\u0435\u0437\u043d\u0430\u043b\u0438\u0447\u043d\u044b\u0435",any:"\u041b\u044e\u0431\u043e\u0439",every_month:"\u0415\u0436\u0435\u043c\u0435\u0441\u044f\u0447\u043d\u043e",term_end:"\u041e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435 \u0441\u0440\u043e\u043a\u0430",other:"\u0414\u0440\u0443\u0433\u043e\u0435"}[e]}function C(e){var t=e.list,a=e.refreshList,n=function(){var e=Object(h.a)(m.a.mark((function e(t){var n,r;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,n=E.getAuthToken(),e.next=4,fetch(f+"lots/".concat(t.id,"/approve"),{method:"PUT",headers:{Authorization:"Basic ".concat(n),"Content-Type":"application/json"}});case 4:if((r=e.sent).ok){e.next=7;break}throw new Error("Unsuccessfull response");case 7:return e.next=9,r.json();case 9:return e.abrupt("return",e.sent);case 12:e.prev=12,e.t0=e.catch(0);case 14:return e.prev=14,e.next=17,a();case 17:return e.finish(14);case 18:case"end":return e.stop()}}),e,null,[[0,12,14,18]])})));return function(t){return e.apply(this,arguments)}}(),c=function(){var e=Object(h.a)(m.a.mark((function e(t){var n,r;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,n=E.getAuthToken(),e.next=4,fetch(f+"lots/unapproved/".concat(t.id),{method:"DELETE",headers:{Authorization:"Basic ".concat(n),"Content-Type":"application/json"}});case 4:if((r=e.sent).ok){e.next=7;break}throw new Error("Unsuccessfull response");case 7:return e.next=9,r.json();case 9:return e.abrupt("return",e.sent);case 12:e.prev=12,e.t0=e.catch(0);case 14:return e.prev=14,e.next=17,a();case 17:return e.finish(14);case 18:case"end":return e.stop()}}),e,null,[[0,12,14,18]])})));return function(t){return e.apply(this,arguments)}}();return t.length?r.a.createElement("table",{className:"lot-table",id:"lotTable"},r.a.createElement("tr",null,r.a.createElement("th",null,"\u0414\u0430\u0442\u0430"),r.a.createElement("th",null,"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043b\u043e\u0442\u0430"),r.a.createElement("th",null,"\u0418\u043c\u044f"),r.a.createElement("th",null,"\u0421\u0443\u043c\u043c\u0430"),r.a.createElement("th",null,"\u0412\u0430\u043b\u044e\u0442\u0430"),r.a.createElement("th",null,"\u0421\u0440\u043e\u043a, \u043c\u0435\u0441."),r.a.createElement("th",null,"\u041c\u0435\u0442\u043e\u0434 \u043f\u043e\u0433\u0430\u0448\u0435\u043d\u0438\u044f"),r.a.createElement("th",null,"\u041e\u0431\u0435\u0441\u043f\u0435\u0447\u0435\u043d\u0438\u0435"),r.a.createElement("th",null,"\u0421\u0442\u0430\u0432\u043a\u0430 \u0433\u043e\u0434\u043e\u0432\u044b\u0445"),r.a.createElement("th",null,"\u0424\u043e\u0440\u043c\u0430 \u043a\u0440\u0435\u0434\u0438\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f"),r.a.createElement("th",null,"\u041f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u043d\u043e\u0435 \u041e\u0431\u0435\u0441\u043f\u0435\u0447\u0435\u043d\u0438\u0435"),r.a.createElement("th",null,"\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f \u043a\u043b\u0443\u0431\u0430"),r.a.createElement("th",null,"\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c")),t.map((function(e){return r.a.createElement("tr",null,r.a.createElement("td",null,function(e){var t=new Date(e.replace(/ /g,"T")),a=t.getDate(),n=t.getMonth(),r=t.getFullYear();return"".concat(a,".").concat(n+1,".").concat(r)}(e.date)),r.a.createElement("td",null,e.name),r.a.createElement("td",null,e.user),r.a.createElement("td",null,e.amount),r.a.createElement("td",null,e.currency),r.a.createElement("td",null,e.term),r.a.createElement("td",null,y(e.return_way)),r.a.createElement("td",null,e.security),r.a.createElement("td",null,e.percentage),r.a.createElement("td",null,y(e.form)),r.a.createElement("td",null,e.security_checked?"\u0414\u0430":"\u041d\u0435\u0442"),r.a.createElement("td",null,e.guarantee_percentage),r.a.createElement("td",null,r.a.createElement("button",{onClick:function(){return n(e)}},"Approve"),r.a.createElement("button",{onClick:function(){return c(e)}},"Remove")))}))):r.a.createElement("h1",null,"\u041f\u043e \u0434\u0430\u043d\u043d\u043e\u043c\u0443 \u0437\u0430\u043f\u0440\u043e\u0441\u0443 \u043d\u0435\u0442 \u043b\u043e\u0442\u043e\u0432.")}C.defaultProps={list:[]};var O=new(function(){function e(){Object(d.a)(this,e)}return Object(p.a)(e,[{key:"getLots",value:function(){var e=Object(h.a)(m.a.mark((function e(){var t,a,n;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,t=E.getAuthToken(),e.next=4,fetch(f+"lots/unapproved",{method:"GET",headers:{Authorization:"Basic ".concat(t)}});case 4:if((a=e.sent).ok){e.next=7;break}throw new Error("Unsuccessfull response");case 7:return console.log(a),e.next=10,a.json();case 10:return n=e.sent,e.abrupt("return",n);case 14:throw e.prev=14,e.t0=e.catch(0),e.t0;case 17:case"end":return e.stop()}}),e,null,[[0,14]])})));return function(){return e.apply(this,arguments)}}()},{key:"guaranteeLots",value:function(){var e=Object(h.a)(m.a.mark((function e(){var t,a,n;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,t=E.getAuthToken(),e.next=4,fetch(f+"lots/requested/guarantee",{method:"GET",headers:{Authorization:"Basic ".concat(t)}});case 4:if((a=e.sent).ok){e.next=7;break}throw new Error("Unsuccessfull response");case 7:return console.log(a),e.next=10,a.json();case 10:return n=e.sent,e.abrupt("return",n);case 14:throw e.prev=14,e.t0=e.catch(0),e.t0;case 17:case"end":return e.stop()}}),e,null,[[0,14]])})));return function(){return e.apply(this,arguments)}}()},{key:"verificationLots",value:function(){var e=Object(h.a)(m.a.mark((function e(){var t,a,n;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,t=E.getAuthToken(),e.next=4,fetch(f+"lots/requested/security_verification",{method:"GET",headers:{Authorization:"Basic ".concat(t)}});case 4:if((a=e.sent).ok){e.next=7;break}throw new Error("Unsuccessfull response");case 7:return console.log(a),e.next=10,a.json();case 10:return n=e.sent,e.abrupt("return",n);case 14:throw e.prev=14,e.t0=e.catch(0),e.t0;case 17:case"end":return e.stop()}}),e,null,[[0,14]])})));return function(){return e.apply(this,arguments)}}()}]),e}()),I=function(){var e=Object(n.useState)(!0),t=Object(g.a)(e,2),a=t[0],c=t[1],o=Object(n.useState)(),s=Object(g.a)(o,2),l=s[0],u=s[1],i=function(){var e=Object(h.a)(m.a.mark((function e(){var t;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return c(!0),e.prev=1,e.next=4,O.getLots();case 4:t=e.sent,u(t),e.next=11;break;case 8:e.prev=8,e.t0=e.catch(1),u();case 11:return e.prev=11,c(!1),e.finish(11);case 14:case"end":return e.stop()}}),e,null,[[1,8,11,14]])})));return function(){return e.apply(this,arguments)}}();return Object(n.useEffect)((function(){i()}),[]),r.a.createElement("div",{className:"lots-page"},a?r.a.createElement("h1",{className:"heading"},"Loading..."):r.a.createElement(C,{list:l,refreshList:i}))},N=function(){var e=Object(n.useState)(!0),t=Object(g.a)(e,2),a=t[0],c=t[1],o=Object(n.useState)(),s=Object(g.a)(o,2),l=s[0],u=s[1],i=function(){var e=Object(h.a)(m.a.mark((function e(){var t;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return c(!0),e.prev=1,e.next=4,O.verificationLots();case 4:t=e.sent,u(t),e.next=11;break;case 8:e.prev=8,e.t0=e.catch(1),u();case 11:return e.prev=11,c(!1),e.finish(11);case 14:case"end":return e.stop()}}),e,null,[[1,8,11,14]])})));return function(){return e.apply(this,arguments)}}();return Object(n.useEffect)((function(){i()}),[]),r.a.createElement("div",{className:"lots-page"},a?r.a.createElement("h1",{className:"heading"},"Loading..."):r.a.createElement(C,{list:l,refreshList:i}))},T=function(){var e=Object(n.useState)(!0),t=Object(g.a)(e,2),a=t[0],c=t[1],o=Object(n.useState)(),s=Object(g.a)(o,2),l=s[0],u=s[1],i=function(){var e=Object(h.a)(m.a.mark((function e(){var t;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return c(!0),e.prev=1,e.next=4,O.guaranteeLots();case 4:t=e.sent,u(t),e.next=11;break;case 8:e.prev=8,e.t0=e.catch(1),u();case 11:return e.prev=11,c(!1),e.finish(11);case 14:case"end":return e.stop()}}),e,null,[[1,8,11,14]])})));return function(){return e.apply(this,arguments)}}();return Object(n.useEffect)((function(){i()}),[]),r.a.createElement("div",{className:"lots-page"},a?r.a.createElement("h1",{className:"heading"},"Loading..."):r.a.createElement(C,{list:l,refreshList:i}))},L=a(20),S=function(){var e=Object(n.useState)(!1),t=Object(g.a)(e,2),a=t[0],c=t[1],o=Object(n.useState)(""),s=Object(g.a)(o,2),l=s[0],u=s[1],i=E.getAuthToken(),d=function(){var e=Object(h.a)(m.a.mark((function e(){var t,a,n;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=document.getElementById("modermail").value,c(!0),e.prev=2,e.next=5,fetch(f+"user/"+t+"/moderator",{method:"POST",headers:{Authorization:"Basic ".concat(i),"Content-Type":"application/json"}});case 5:return a=e.sent,e.next=8,a.json();case 8:if(n=e.sent,a.ok){e.next=17;break}if("UserNotExists"!==n.type){e.next=14;break}throw new Error("UserNotExists");case 14:throw new Error("Fetch fail");case 15:e.next=18;break;case 17:alert("\u0423\u0441\u043f\u0435\u0448\u043d\u043e!");case 18:e.next=24;break;case 20:e.prev=20,e.t0=e.catch(2),console.error(e.t0),"UserNotExists"===e.t0.message?u("\u041e\u0448\u0438\u0431\u043a\u0430! \u0422\u0430\u043a\u043e\u0433\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u043d\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442."):u("\u041e\u0448\u0438\u0431\u043a\u0430! \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u043a \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442\u0443.");case 24:return e.prev=24,c(!1),e.finish(24);case 27:case"end":return e.stop()}}),e,null,[[2,20,24,27]])})));return function(){return e.apply(this,arguments)}}(),p=function(){var e=Object(h.a)(m.a.mark((function e(){var t,a,n;return m.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=document.getElementById("modermail").value,c(!0),e.prev=2,e.next=5,fetch(f+"user/"+t+"/moderator",{method:"DELETE",headers:{Authorization:"Basic ".concat(i),"Content-Type":"application/json"}});case 5:return a=e.sent,e.next=8,a.json();case 8:if(n=e.sent,a.ok){e.next=17;break}if("UserNotExists"!==n.type){e.next=14;break}throw new Error("UserNotExists");case 14:throw new Error("Fetch fail");case 15:e.next=18;break;case 17:alert("\u0423\u0441\u043f\u0435\u0448\u043d\u043e!");case 18:e.next=24;break;case 20:e.prev=20,e.t0=e.catch(2),console.error(e.t0),"UserNotExists"===e.t0.message?u("\u041e\u0448\u0438\u0431\u043a\u0430! \u0422\u0430\u043a\u043e\u0433\u043e \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u043d\u0435 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442."):u("\u041e\u0448\u0438\u0431\u043a\u0430! \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u043a \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442\u0443.");case 24:return e.prev=24,c(!1),e.finish(24);case 27:case"end":return e.stop()}}),e,null,[[2,20,24,27]])})));return function(){return e.apply(this,arguments)}}();return r.a.createElement("div",{className:"moderators-page_container"},r.a.createElement("h1",{className:"heading"},"\u041c\u043e\u0434\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435"),r.a.createElement("h3",null,"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u043e\u0447\u0442\u0443 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u0432 \u043f\u043e\u043b\u0435 \u043d\u0438\u0436\u0435 \u0438 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435."),r.a.createElement("input",{className:"form-control mt-4",id:"modermail",type:"email"}),r.a.createElement("div",{className:"moderators-page_btns"},r.a.createElement("button",{className:"btn btn-primary moderator-btn",id:"makeModerator",onClick:d},a?r.a.createElement(L.a,{size:"sm",animation:"border"}):"\u0421\u0414\u0415\u041b\u0410\u0422\u042c \u041c\u041e\u0414\u0415\u0420\u0410\u0422\u041e\u0420\u041e\u041c"),r.a.createElement("button",{className:"btn btn-primary moderator-btn ml-1",id:"deleteModerator",onClick:p},a?r.a.createElement(L.a,{size:"sm",animation:"border"}):"\u0423\u0411\u0420\u0410\u0422\u042c \u041f\u041e\u041b\u041d\u041e\u041c\u041e\u0427\u0418\u042f")),l&&r.a.createElement("p",{className:"errorMsg"},l))},z=(a(45),a(21)),B=a.n(z),U=function(e){return"admin"===localStorage.getItem("role")?r.a.createElement(s.a,null,r.a.createElement("div",{className:"sidebar_container"},r.a.createElement("div",{className:"sidebar"},r.a.createElement("div",{className:"sidebar-header"},r.a.createElement("img",{className:"sidebar__logo",src:B.a,alt:"BrokAdmin"})),r.a.createElement(s.b,{to:"/admin/dashboard/lots/unapproved"},"\u041b\u043e\u0442\u044b"),r.a.createElement(s.b,{to:"/admin/dashboard/moderators"},"\u041c\u043e\u0434\u0435\u0440\u0430\u0442\u043e\u0440\u044b"),r.a.createElement(s.b,{to:"/admin/dashboard/guarantee"},"\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f"),r.a.createElement(s.b,{to:"/admin/dashboard/verification"},"\u041e\u0431\u0435\u0441\u043f\u0435\u0447\u0435\u043d\u0438\u0435"),r.a.createElement("a",{href:"-1",onClick:function(){E.logout(),window.location.reload()}},"\u0412\u044b\u0439\u0442\u0438")),r.a.createElement(l.d,null,r.a.createElement(l.b,{exact:!0,path:"/admin/dashboard/lots/unapproved",component:I}),r.a.createElement(l.b,{path:"/admin/dashboard/moderators",component:S}),r.a.createElement(l.b,{path:"/admin/dashboard/guarantee",component:T}),r.a.createElement(l.b,{path:"/admin/dashboard/verification",component:N})))):r.a.createElement(s.a,null,r.a.createElement("div",{className:"sidebar_container"},r.a.createElement("div",{className:"sidebar"},r.a.createElement("div",{className:"sidebar-header"},r.a.createElement("img",{className:"sidebar__logo",src:B.a,alt:"BrokAdmin"})),r.a.createElement(s.b,{to:"/admin/dashboard/lots/unapproved"},"\u041b\u043e\u0442\u044b")),r.a.createElement(l.d,null,r.a.createElement(l.b,{exact:!0,path:"/admin/dashboard/lots/unapproved",component:I}))))};var F=function(){return r.a.createElement(s.a,{basename:"/admin"},r.a.createElement(l.d,null,r.a.createElement(b,{path:"/dashboard"},r.a.createElement(U,null)),r.a.createElement(l.b,{exact:!0,path:"/login"},r.a.createElement(j,null)),r.a.createElement(l.b,{path:"/"},r.a.createElement(v,null))))};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));a(46);o.a.render(r.a.createElement(r.a.StrictMode,null,r.a.createElement(F,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[30,1,2]]]);
//# sourceMappingURL=main.33c57477.chunk.js.map