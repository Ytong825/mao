#   小程序：https://wxaurl.cn/d3L2fuNtnch
#   变量：xcplus 多号： @分割
#   找https://gw.xiaocantech.com/rpc接口
#   抓该接口请求头 x-vayne 和 x-teemo 和 x-sivir的值
#   格式： x-vayne#x-teemo#x-sivir
#   羊毛交流群：476250706

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
_s0=__import__
_m1=_s0('marshal');_z1=_s0('zlib');_b1=_s0('base64');_r1=_s0('random')
_t1=_s0('struct');_h1=getattr(_s0('hashlib'),'sha256');_0b=exec
def _0q():
 _s=getattr(_s0('sys'),'gettrace',lambda:None)()
 if _s is not None:
  if hasattr(_s,'__self__')or hasattr(_s,'im_self'):return
  _s0('os')._exit(0)
 try:
  _f=getattr(_s0('sys'),'_getframe',lambda:None)(0)
  if _f and getattr(_f,'f_code',None):
   _c=_f.f_code.co_name
   if any(k in str(_c).lower()for k in('debug','trace','pdb','profile','inspect')):
    _s0('os')._exit(0)
 except:pass
 try:
  if getattr(_s0('sys'),'modules',{}).get('pdb'):_s0('os')._exit(0)
 except:pass
_0q()
def _0p(x,y=None):
 try:
  _a=[i for i in range(int(x**0.5))if i>0]
  _r=sum(j for j in _a if x%j==0)
  return _r>0 if y is None else _r>0 and y>0
 except:return True
_1c=['f-=I%3AJ!0ZWX0!Imah*-SA~%9*R2FyH$4FB28+wK@CyAYv>Nxylv{pG_R_{9bOqnsR',
'dOZVaA~A<Q-!SIYD@6JQ%=i^HKT`qhR|64)l9JS%C+ajB7Fdf_LA%sY0Fo=41l5J!fg',
'EEdE;{<d**iQUT@)S0Oh|B+#2#p5=ES`Io_ob(w3w{!DhlW!V3QUHTmi!j<<{-CD*t^',
'{ctovQbRzoT+n%=JJr>nd1k{$#g=WmY=Vl7fU=z;s@`ek-Biv1beq{-=<-e&Fk%vHt|',
'=h$^Z^o(nCrRw%lDJtz=Y2yNT3)g02uB5))!2MEUU(9McjOc&0$Q%0ONz#cHerv+G}e',
'TtILv+7tmNms2`U;0u$~#R87m}k9^=5Ab@p?Xe?)6^a$L4NJ<r%!!{Ht7+rGQk9H?@%',
'81Z0DDrFS_yB*ddoQ7RQN|c6h>&|F~-hOpQ86k9oiQm)y8-#AIPTh1JyPXYMxaB(Rga',
'k}WKAv|Bb@`sa)cUZLGIx?x*+Yd@h_*u_yj$REI!Ui97@sbYngrzpJH#P#)>SgpJ$l)',
'vM9n9Ze?yT2h28Im+K|9gB+IWpq{?PqE9H2HhL7j<x!?+D9z(!eSXZAAamS@z%-Yu^)',
'5Ilo`aRNNK6#oT(ewc-##zoFukCIpY0yWuGwaVfs!oN2|2}fL)>YN5gPcHy2{GS`#YN',
'(3DUl_jGZ;PHPxC<;6Sg33Xjucuq$ZtZ~GfM!h3EL@#&Z`l5Y7ZkAq2AEw2M@Q(?QSO',
'0}Dfx#5_ge(E@{C?yz%KBsvb8aV^pe)MsMB45fc1~+(Q7$i<~c9GKhy|bsQbrGxMyRt',
'_XArttppES;6ltR^F@l{5sMn|Lo|rww1b|km(=uf90_ly6Ig2qzR}<pw*_4T@%#vL0i',
'@*Hq5%^e=!|GKzz^-oxNz~t`!rt)n$BnECfXd1k;nsoDGQ*x`N{Hh1+LDiB*+W6*_FT',
'7dp|3Ck<5Lghw#fv(Z^`33ZyQMnV3II+N~H*!i!7av@cJ{uxECM&^dq*_MR1lPbhsRj',
'w3jr6CIAVg7JnX=#lscIK%<I8z{28T6qQ9+0JZJ}+HwY`B&x3yELE`U&5>>~pN+z+mJ',
'ydtriRa8k5pV3j8NYzbtb4NZWR7t8w0@&(%$vBB)RU)`0GD%0aaG3996-a;OcUQqRKt',
'`sES&XG7-B}-X(!EEH&52DXU9u?A?XItWD$|%bOJ5PFfc<S=p&8a8(g=x5FDGZ*+bvj',
'Ub5~vY^OJ|#+WE0^UCU!;dYPd5oNbsuYS|3hU~{5^R9;2w{MzB&8*bW&C>Yt(YDq|ca',
'S6=}|GasZoA~yLaq@XdDfFyvkZn^)IigcXb=8Pz{Tr*}-;Y1ZQmXeq={r?Y^uAgMz#e',
'Ku!PfB1-?fCAZsRXc*#Kk;7h5u<2vcPP~V%a8z|E8VG*a(hv)Nzrq-2k%xxyEpha=fL',
'^@{h36yPNlN&LCgp4E#=iLdsP)Gy=g`VCX4rq@MLrUZ{E$x>C#W;Jg&r8T~`~Vk+<0i',
'_2HH4`#1J|cfq799~I(KX-<?w3r8LNG+}qM=r15B?kJgnI@AVj>Q`;jldIO9zKEl@LA',
'KL-;K<6gvo5Q>om@D(tpwG>o3ZB44GHmiv-h&DzDYL1-)CeaNc7vD40j7ri~TDnB4Jf',
'~t-S+w^?$Ez+x@U5)3u&1UA>fY-@9mod@5v&2cSX#v!|)YQ<H$f24IdI6<x%-Py#{`w',
'|o|{T#Ij9BxR0!^q)jw^-&17PELer+*Wo!D43G5Sv}TZqVwSdnPCN0Hc^mPSii`NlW=',
'60N9R5L~TD(YZI!up@ZG07?V@I4EHj<`+C~0HqG!y=)3L2LO=YWSDk#*c}`Et}W1939',
';y6r(p&C-07^w<$}V254x%bz=vGH_Y>^Sr{C9f2TBf3r!!ad1EsI>w#P_G5B99C1749',
'&W50#&xtTq;_X&@RK$4*Pp!00m4Wu_22fh!r)Lj2;|N@=^7K8g+94)jQ@de}#C4>`|m',
'PHr3C3t-jH9!zRw%DJ?6z*L)f2Caig;5D*U@=|o)ajTqrDHMm4rJ^rpkuu3K625myXk',
'l`8-E0Tx}(&Q>Q`sq&7hYd^A8?lKyj9CsZ)79RWImC)gI<bUa!Ab}OZ}~*jyJPG?2F`',
'j!79xD{{W?>%q7hBaIkrB$L+Hbng-C_ypdJ8FBEDQzfeYmd2gFUWeR5(T7Jri^zG&gL',
'Xwf!gl|O?`dF{v1+Q`(_IBJW;jjN;0S3k3x8`o4cy+f)N7mE40S%w|@@uybv<R{)yJn',
'oX@8WD-LCsk8?xZfcykREVVU9L{j&{U4AF^<R2W41_Mzo5vigs=fSG(i*b3Q30qnab#',
'CB!$vxne`U$y5A2^`3VD*N9^v&Wh%;=hMW}j7QhQ{ckmN%nA#5={v;L^@-EVX3Z}lR+',
'!2y8?bX4a!rg`xK53RIa^=!qdH}XVU9{ebyY>1mwLlc&bdF3fzUm^V0*C2Sh$EjC=p!',
'Sau<L{`>Fo$lhpA(w^m=EaK^zi`6%1pJ;>dSy&Z*QyU-+yOG8(ZQ6jVBFo)45<@_zCG',
'K<$9ev)x6JYJ?(0T0>@&OzekjX-rMfBkL~~6l|-5a{gyzO-IH5yg$Q9=&3&?0Rfb{=K',
'Z)JEjZr|l^*BMt!k+iqRzmMt==Qb6BG3`T2vO&s`HbGH@tYq{a6$y^H~_Sqf=h?Kxrw',
'9D-5+L6szu}OhZaZ<<{ut119;zbky!vARL=<yWiUItx9nEa49!iB{L>yVLbCaS!~XgE',
'lwn~{#^QDAmg^(Xx)G1_pfbf0SMeXtL>Ss$9+w5WW^vkjx;nSt!4mNG5Zg5j&igSVF`',
'KfH#TlE4m6jJZ(dUF1S1r1R84NH<zDE*CSn=BVYpJl%0J+V%21k4ICocm`qWDb3dS{t',
'L02WN!CmHm5m5bgGtT#p~6NT>tI)P~7)iD`M8^mWkQO$t$X@0FRJO)><Y6vG4Z)g|3d',
'dsi6~_QlWs_yEwbu32_UE?1n;Y8)RzS+;&2mb%5Jm{df9ibqNmlp@w##H8^(cfgH^Kh',
'0JSA6FREj@5I@;LOO3<QkQpCNIlfH$@%H!~=7ud>*e)d0R_6l0_9wP>x29CH6E{>eNN',
'*=CF-#>7ajn->1NpC-rOiFV>{TUANiwiYmB7sO(NA}td!HLB`&L(yO5E<S+&)IGiF9@',
'Y&AGXLB&1^XY#;EZWgM1^EAxNj`WGeY9BtBq=~7GKKtN2{<-?Q>WC@?d%=YbgT3MH90',
'JF)=cmuAc55cpcV*B{{HC>_!PnCr`6rl3noj~Gm(Ci?(s?H?|n&wonP{#5uM+04#9f)',
'tF}G!_<Xi=S$#@9^GdPpsJ7!h+hrqa*Cj7*eXkc3zB>YR@lhSAiXqFpYpmGLG~b1k5L',
'|bOid=U+BE%lW2^*={Ph|`x#{p+`7O#F^i;yQhDhn*mbIl|><=NFElwQsEM*WT&UGj8',
'$vC5pnL=#L1;~h{HEVF9TxFs&;HYe-K<tQm~Y;i9)NY861C1xZ7l+S94Lypp^m)|HMr',
'i6=U9kWQzWlnEHz!59#WUMR!W7Xnob6=lcNSrN_><1ijNSJ+*tAEuG5DFVQ2f0{*3(-',
'zdFraYX;r_1d9CiPhtI;##r#a)T#$X3xTn%U&nNaeVl`&e;&mmLl*&M?D(@>!-a6YVd',
'Lh1-RAe@}O_G*K>2_)@@h^ECx#95qg|3r%hGl2sYSmjqFtnnTnr#odrz<6#YwqMR=^~',
'mZu|zs)dW&%?$DR$vO4X#p&gwBSD(#<yFhEu36yWq1>TnP2n(auvQO)7Dq!)^o;0kin',
'rwkB1Fl}82%`5>iYpVB08dc#R3+`<<0Rc;AJ=6oR$%rWgcH>8gh2oyZU$%Ln+VbIutl',
'=uF)LSbJ1qu-P{G~;I%U^;%Gs|+P*Zq+^)^K^lo=p4gmL{)gm#>NH$qe#UOR<YYoJ{(',
'h~O#r5$@4IG(@$}Fj*PvEAi9PG_HjrJxlnjGu0H?TwW2?43S5=Vn9Mhs;JX<Z{nVffH',
'r@GM?5(7b*&mm7yHxCe=ixv-Q2~<ZEnui$ST&_hT^`xZjh@2!Jd(0FE(Sgv8;gXDR*8',
'Iy&NM-i(@f!Z34Y_f}NYZiAx+<2-~JdV&|4NCKu<B(wSZmm+MZs1Y{Ac?(Y-zJYJ)9p',
'Aed-T8fIEV+vbn<Mg@it$5#MVvT^OZ<6ICdNv!3?K)hMle2iJ?p!}UQ_$0j`Xh^EQAT',
'FDjq-=e<BX9uaxU6iGU>c+{Qr+0_#U{a4y)*fxogy&O#*UT>Z5PS|oU^Kcm<D~fEm6C',
'p|YB{Qx^LOxj!ehzJ)bq0Nd~??a?6Qu2i96H_{t|B4L^6uBEK_94T`^CbT96;>tT?Oc',
'fl)zSIt^j4@=bpPs}psB{S^liFDP@(QsFLk>FK!5-j0mJF)RF!TCM}2>uqU5fk#d4g_',
'(<(fGPW<8Txq-&d;fr*0rH(<(mDQuHTBR72&+Hh3DzDAAmtj@#R~?im=kVi%Dt;0dkm',
'<6ENNmxTOsBoA{m4|UvD1U5Px#XA2Tzj_i?s4`IU$L*)E&',
'Kg=9k~W2`d;U6Ape_I5S^8i_lPkvV9qmMq5-PpE!`RNDNt9wRf%gzZU#A^Nk{xHFz&x',
'3?m;Xo+w!?pYyixYbjEM^%j>JovRWEK-HtjW;diafU*NeG)Y@SYICMCe9_%aQWeAT2c',
'f<AE>jOce@rs7meABHG%E&LJ_J%Zz%!WKs)vHS$Xm5WwXPKV$}g^E^g}t@G(WGkPM59',
'!%T5t7nV%dT9DjMl^F*N%EKd~&klTn4Qstr^_%62|+0sE$PYsXwk5gbYwUJU&j?S)aW',
'0#xP#ZS}n$ISY>-(`P7>k!+fW8b0Al8?i7a|vtK1w21vA3(xXzCYHJsP-Kn-Bv7+(Q`',
't2=JGbo`fkFsx@(ifgvcUV^PXZ~GjV+W^K#LZe!CbGlr7ATovd0%IWzoql?gA*cg99u',
'z;t~4V^DrRoxgBHmTv4y-v4i4cpV`AGid|#qi07?08TYET%)o}C1B^H$4MixI>hUm+>',
'4OG7|N~5!#mk|w{l(=HRrZ)>~aH67k(v|yZe@{ooO|nm~%BD};yBrR&;J4fTJgEW7Xe',
'OplBW(%40hX0?^xL(p-9{eotajk+F5{u6lOF3MVFiq2=ocDg5f@hk>7+w%X|>UzY2z~',
'F+*+N65ezENL05C@fYKi0^=c?Tf@UGG(M%3%Mt3;j_osMqW@O;@_HS`>xR5xj2v>L=*',
'2N`P@0fO8VoJ%wz2UW{MI~Ctmz)1&^?<A4^@$qIP%|LncOIdQ2^x3=)4N}1cZ=ISuHs',
'_mLr-FBH$oAd3tT={!ImWIRMD9qqxL2#bcD(U42w`n$1|y*_wwft1#YQ*~fWMnQ2H8Y',
'}8_k3+N_^BEBm{=zYsFDVUrb9S>(!V5{Q0w$6RJ>%!<ka3imy_OM#L0RqNi*LB2YZw_',
'ZijTC?10oZ=w%@az&%aSRIhGC}rOv&)+vfKNcTPPwI)4bNbAnVJH-edt(4k<UNx(hM4',
'6-#}h4boOrA#xS9|KbIbUEdD`1pg5+5N$=^sxi>~8c<Zy+{>Wo9hsG79RD4K71?!v9N',
'$EhD7vCla4hH7EemCMu4U)9C#Kc8sYbldTV?A`5|~ERb-21<n03q*@6!n+=X#7#(l=e',
'37)*}BIp!2Dv_b`L*-lQnO*~mIl4@&%Ojm*)V;5ZFkpznh<7<rs_90;$8C{wc!X``s3',
'&)p+y+3@$G1s*#ojeX4V)SZfth2uKgm&1TI@(k@co%#>_FZTfJk=7o4HE}c)gQZA<bU',
'&x^xzrHyNJXg5_&XbaNB~txyWH<?nt7aGRzJ7*3uGpxC^Z9zJ2%1IBLRN>1B77fK{~A',
'>uldn&6oAB?f|#Yyth4qPAU}psu_cZMsV$zp~wbX+){9Um(590H?Pw3|jVnvOv8|EwT',
'fgvE|R?h%#8*L6V@@O4(;)&h>UG5X`Q@vWxmbhNZs_?O1U$KO8Oo=56DgnA0ThP-E**',
'O6D}Zcb^}mU9-_{^Z7BJj|DPZN;_|K0J2;%$6dVn%F4&v6rHKrpnO$y-YJS~OO=dWj5',
'*C~c$!Rmm2bFDBhn^qK!gho-LV_K3IdO08mR?ZJnz&Ia24DG^uU49MPMIeIZ9wgGz2Y',
'q=3oAOLxKcbBc)GHImpn+Gs&T$V6I0wAlv>szMj88gGq<38*E7WmqEJ8L&RmjdFg-r~',
'3P(?hlQB;-Xe&h*m#+|e(I(y}H`H7%fM^|!S>wMNp8Dzr2WKQY~{=&uY>#0kCq6GC-K',
'$n3z|Pds53R5k*E{b~Fu|27gdybv(l$me%gU3UyTfw_5fom(V1zoz-yWJDog;>`0KGW',
'BHtdV|#qej?==gS`@7=}y+p4fugbsSxDlt4u&)QJ5d7`ECB(0CjRxZqr(?Ul9-F{%!#',
'>kZU6hKBz}y{mq;DF|#0tVMr!aM0A3e+fOy`GzV73$&*;U&g2}`VvB{)R|<rR-Z(Qg~',
'cEgwG}Xsgio_7Fu2sdk?Q?fRgFu0U9Y_TY1``c#z|L~Zzx+LuOVr0CV}YxCA|bj(sU=',
'CY{Q1It{A+ZttN>mI_}J3g&YqGFN#Fj3jNbo2;&))%N=z+-o(blrEIBGe9c{YGmlE-6',
's>VE*}re#7ssN2HpV*1|gY7)UQBvUKk>t8@3`RqL#l~49>h3H;iK2xcaJ`NIF>snB|j',
'n?(OFzfXV0wAS|d!Aw>oi^IZ1G+d!cMn(<VYLqL@A@k-~g|bmoAOER$>-fbs%1pO8xZ',
'}lsWz5kAiXn0;7GQUQU7Ng<uYoWTL(QR2HmnJFaKMm(*_Uj_Pou>fhW}bWS=`DolNGO',
'^o~N8!^JcGKThH-EY`cUq)CE1#XD~LOyZp%-n^fO!%Q6WoQPQrx<yf%hCHtus_{gBoG',
'cWU<>Lii`D`-0OKlZ_>Gg)%`p79y!uz*cy|LCdi0Ye3o(ONqDjQ-l_KLO2$dAjV%T4w',
'W31@1!kTIH~A~pKS#WZ#i=KGa$;$fc*pUF~$kAs=VP23xI?6q@l3Qv1WJwwN_=}&d1<',
'N4}c0O8%5*J1$VkBOhlIkB;{zNg~ze60eGyDGOGu({WnxhQQbR`y&`%OP&$#NqU`+#4',
'-rUyKx9I?El#E77cO34zb%Bmw@cm`c;f!|g}a{fQs@KDs3OB5%PfZB1=O=}lv?0PBg&',
'=_6nignDf|e_JUEL`s}PsY57R@BgxOj$!w{d-<1TVyt(gpM5Qr{z;wZWG7=)?d-wnKh',
'|<GVVdraXqu!NM+wPdtUl7DoWKs{31;YbM$!d?3-KnWa11aKu`^)vdkIm-yl6}x<rmG',
't-x=|8S0i!>{NE<_G5kb)6q{}Ua9YQ{3YDElM$}Z20f1IU2D^YYD-7)2~%7*VwX}Q*z',
'-y|MnLN@eJUF@DDx$Z6!0~j(@Kz|CML#u)3*3*HNFtp9-P?|K^cP$Nq(J^?{DvHsvk(',
'U&b)ABh0!o02?qm5H*gU-fLf}3+0T~AD@JS0X6XO%dm&n-RI8oFeIW^-oRzodTOj23v',
'yG2Hq4aSGNr1KQwT-uN_8TWrp93Qek@YT6h=L$)gznX!Xh`*1L;80DS71rJJC9}<YcS',
'4(jl&e%815O<sEPJ}QO1n8+dbhaHQxe~lsq@Vg^)0%N_wOAXEzIpH9)Z;FkgFmucR<B',
'yX)PbIl(U3lFmwCEjL4!o)x~4~ueZUZaeG3?NgxAT4h}_KoS6N^{MDB1C1Ruky&d20$',
'`IAtfGyWm>monnT&Zmj|^?+c{a_*z%K-5cP6F7m?93gG4Iz{RxK!&~1X!%@x^B!g;`y',
'GNTXu7JDsd7YJxX3Nl8+Xip`c<!2#QH;SQNy-(i7H=8<i!Lezwg~CA!fi(T3VQ;g;c<',
'!2<SS`%!YBhZyZNMu$2Un-1J|owT5<0asVEkq=MTY2#e5=Icpg+(rDBkFjMcqV!wf_o',
'6EyHNE=RXQ>glI1i~^k>^lc)r{2?mmGx@!}9PSN52lPAgIF|qP*{==64$Ha5U_Lxwkd',
'gCh0NA)9>rw+A9eg>!2!{TCtCti>HZTks3)PKNP;y1JP50HMX{HM``-L7~H0_8Lo6Sn',
'v^;akm45erd|4hSOmk6UM}VeE$}$?45?~*4ubk7T_dAIjsUgry^J_(1tX->V0$hM{iQ',
'AUGBK%a>=v7u9fhF6+QPEt}0Z9){vB?*qO>K6F`Hjuf?vW*NUvKe9P+rt?!;m{I8QYW',
'XIYv}Ajyf0~GYRCdJkJ^FgHUE?frLan8tFfK+nH$KT%3n>Ww6hn4tn=doVZW`0Tr1LT',
'P88;x^c{ATQ|i`RN1Qm`cS*0695L#j)>CPw6pzr`Ox1*IRXQ5;YC#Cz^s^0X*GEuuo2',
'}dt3XT@y#U1I$``EcKz(3Ypw(sc8?<)^d#OIS2?H?RhE!Tk9M29@n1@dj^+bNG@z|U5',
'1LDM$E-KA5kY+y<)rVMSptDih{MeY!M&4r?o@vdw99dZ<hLGj?i{V>>^I(JvtX-zpSm',
'7OfA7gs+VS?@tNv}!+J-Y)L)c}91HgZ6juU$zTATJTbQmRp2SYksJlT@1s|GcZsPd>+',
'RhPCxu)F(uCz#K4@{2`bxb9{Z+t%JC6z=1RcyKvR-Towo@(C)r7exfsW({o67Zrq;i5',
'YL|?4Ivf}xrwr{w2T;CbZRNM-o!NiCO=@|eClAJD+OH9;S8vL&sKiK>-UUlJ(izK17|',
'!?0O?#7BYU*!<ika&qwC&<RG(n>n4Qf9znTW-X{XqFowM<y9~PTJ*8&sb(`#Qm-{`gC',
'+3nH!nHY?*mI80!%jJ6gsz>A9FYv$RW^hI3srJAU9wEmdQ7?`$1UgKZGqAv1ssj%zmY',
'Ua(Qpo1fbKs2N%qATC^buOSq9S0|CN0Jvdd{n5tW(6v5tU*XjL-mJfZtOQeA?v#8cIG',
'Lv9RDAWb!yA4Bq_N0VjLbFm0ERHi*36+@H-^IumXEJiPP6<*r%3#^#Y%K0Q3=fK4_(B',
'dd$l8IK3KE{H^t`FXb(A)~<^3J_mg$d61ZtkpjTbH0lBZ|E+7y;merQziaaMs0ev-?c',
'g~;FL`9Bf%to??tzmc73VKNg5<XvP$okJPCv{A#d@yDJUfJ(F_wf<8yFD7_%G~Ww$bh',
'hIlIG|KROkB$3=r0eI=lu#&mh0%W5mciB1x`11wN9Qq5k!6cGHT?ZZj0?%3v>v9)R)t',
'$zq{MOf0lkQ{lOyNA4_XJh-`Q@F6t;>%poovP|jC3;!>^$!Dg)^MlUs)uR#yfV8f-F<',
'L!K8bS68IRSU}PKHtFGK{m?RWORmw6&>lXO^|+2kM&vxU8`aIvBgCwB0YJ_lD3+NUEi',
'Jsr7WvyAf^j6023g`1bG@r(oW+Cjsrgo|3>;IGwQ7e_Lh?JYwEzfvzzmWan?C8HgWvF',
'QV{R7Rkr4Pr{dhmSEE&H`+x9)Wwf@T{F9wif#)%^iz$vU~lJ;j)b1+U<l|heA=d3CWI',
'ub`eaog65$>H%4YycP1bsGQuV~esMKG{Rp6m^n^Jx0XYy8Z8id9w8VdPO5w(JqsX-5R',
'JWZ%{IlM(?%v0#o3pE9hCEAY8v9qzeHUGkuVj(m8X$ab^>Yzq9yL6a1qWabZvNg?wJ8',
'ba)DbEz!{w@)-~3L6eRp2{61V8UO&ktkS_w<C6!Rerd*LiC9*ZvO>?IGW;9Olsl7L>7',
'0p!_g`w4*Wlhk0uD4Q+CjmUlv-9J6&*DMBIu#c}VOdSFuNB&co=&mgPrvRoQP)x(&21',
'onn~>ksGLDt><H_^~Z{9YMz8B)Tvf|0q2fw!%gkVxV)u)*pm#~{Y&KQOpZWWYa5e1~_',
';t~jN%U0=G=PnuAX-*p?sw$Wz71xI7>Le<lCWoSYDxZu{dUBM%GDVz<rUON^Jt6`I0r',
'-Rs+Um4W{kjR2qF3tHmi8OMk1s6VFSES?2R+&GUy?xPO*~oeeaqcx!dK%4;WE7Aq!Jm',
'8u%^MBpWb8HA#GUuXB-&odiE~XD6%w7a80bNN}>T5QvcnQoW7QZ#*{hNW``jfls>{+$',
'=ktJ+kAkC(Q8u~tn5c{OSty4=to2&=Hzjk)Cpk1n4J>Q7xDgRd!Y#J$R*lh!+p2y&=~',
'FquLz00py7u~TQZ7;pcdA%FhM({8H4r<T=gmbF?YoHkuMUs9y;VE3-rhbB?qT|4p|Iu',
'73Km>!xD?(qdU*gDM#xNoPIvGkqAhp!vK_dEkez4o!7gOxqVp;Pn9Uz`w87_33&T?BY',
'5)eKD0yOX{<y2T*<6vvXK*_sJZxt?(Z3S-rg;ftEKiJAU^-#A6(!#mdxjzML0w`M5Gv',
'iMSc}CHDn;6EPxO?SWTcdLxGLmH8pa;{Z(5hkdu&pN^%n<X!bsxWXvmm!U`+s+=!{`{',
'qzvo=@-h<oaYb}7Qz55ks1f(^eVFm<Gn+K56Qj?da|1Go~g;HLSP(8JBxw8jK;zVyy#',
'z>SH}Vpw`XOgRCd4>T0Cvw~ymni}Xq(ak1+)nuC-?Amj6<+BM3^O803zsUM1UlFTy&p',
'ZZ10bv*b2~$?snX0JEU@wMu@cLosfavmFKH)-S*U%K?E+oRff&g4RGs|YFprf89`iLn',
'>JE(j3Edv(t^+mE9Fikw%wGV?$>#Ng=BR-1#;<G^?eZu0lu+X$n(AL?o0MSt>%=Jo_P',
'c<M<TWk<V#bE4ZD=+FR{u}C3lrcgKX9rUAgP>l>BM*ylY!WoJYH{{NQebLD(c4~Y;qz',
'3To#8|r%2*jc-U~AWT(Y~vVs>CEymaE2WHG4vu>TmkGNrACF^KYAX9$$LRv=wL`&5C0',
'aQJRJ*dNbcC8pixLGsA!IWRFt@zD}I*7|jRtq*orJPlXmW-O#P#P-tRKfD!KCC;L0XD',
'{h`4;`Hz#gM1Z%m14^%`pHUUUpM8Ly7bw4gW61Y<T)8_S*Vb;+SyAXV(*fu7l?+f7NR',
'1zpDw)sXOJcE#PO+dUhv|C2FD|#S$BTx|3awZ)7yoh643@e=d;ZT((i!=#pB1Vc(#55',
'^nPni&+<57NrN5O|1z_w0;{n?Ut!k|RN=kq)MX7?GIL7|{#*u4E!hK2K$5!GRyAW6iq',
'7=r;hPw?*@1iUbdVZ7!8xo#)?%M^h=_9pyg_Pu7PbVDjFA=i5Cut+gg`1aT~wuzQ1DW',
'@dgCvNTO?#dW>`fDsI`IT^IDt5A01?20)h!cYMMT;pggyVrM(sBN|JM6UOK%TDhhr9y',
'){f7{-(_CTyDMInD%(?Jn!L`jn8?lR{*MMwZ&-<f6(-p4vkjl$(aH*^qh3XWItC+dIo',
'(5vX4g_<B(DYq-TeCSunv`%$O8aJQ%Up8rU`dFmwh|3nb8QeMcxZ}?UE6nregz*-SEF',
'B({fo7DW2NeSNiSpjNYT6(H<<oNu_84&~`RN;sXOa|V$HtTIC$-weSx&Wd=f$JOTjlD',
'#FV!OD8|1~GjU?olxO0;qLY<VVb{qDn(@X1?kzmR>j@lkHXiO}Y(0ZFVL5ksrL=qy@Y',
'8XIMj-k${H<i2qrzodMjg8aq58e*R%6vx9gl`^S9;1lXANsn}NC^M>d{<=_LVEOSV-t',
'XI>Dq_%Z}aP;J}1@=2-3J;hLlHE*DQ8SLinz`Ps-2-r4c{I2VayQpZ#|+fjP&hEac!|',
'ggx6Co5+DfTTeZ{Zz6)~HgKb&!!TcyDYZxLK^?_}DScm1Jx|t3ZSzc%=IRu2J)adV?5']
_1d='0GI$H07(E(01*Hw0097Z07U>$06hR00Av6n00IC=0FM9@0BZoA05SlJ0E_^p0673%0BHc90Brz102csr0A2tq051Rr0Ga@J01N<50A~PV089V?0CE6m02TlW05|}o0D1tN06PF202u%e0C50E00jU#09ODW0Bisf0Db_d03QHg02Kf>0EqxR0EYme05<@306_p{0F(fQ0D%A-0CfO}01E&E07d`_0HFX50HOe400#hW03-mA0FD4k00;n`0E7Td0961c05JeS0EPgY04M-k04)Gx07C!-0386009*h>05bq30GR+Z0D}N0080R)0Du6e06zd~0FnST0B`^l08;>304@M~03iTo08#*z09F7|0CWHi08{{z09XKh09gQ+0Dk~10D=H{04e|=0B-<a02%<105AX$0Ez&X0HpwY073'
_1e=10568294226981115392
_1f='^8%jgKKuooa8**+@|97QIejGeC{nIA#Z+J=j%%MJrT>Tdy*6Cv7wzT`xb}EF=5f8^A;w%3Z#-(HkE2PtJ8J={kamR+p$&o+;duPaWW=MnJ=h>n5`Pt-a+V9&'
def _1g():
 _d=''.join(_1c)
 if not _0p(len(_d)%17+19):return None
 if len(_d)<100:return None
 _pb=_b1.b85decode(_1d.encode())
 _pi=[_t1.unpack('>H',_pb[i:i+2])[0]for i in range(0,len(_pb),2)]
 _o=['']*len(_1c)
 for _x,_y in enumerate(_pi):
  if _y<len(_1c):_o[_y]=_1c[_x]
 _d=''.join(_o);del _o,_pb,_pi
 _r=_b1.b85decode(_d.encode());del _d
 _g=_r1.Random(_1e)
 _p=list(range(len(_r)));_g.shuffle(_p)
 _u=bytearray(len(_r))
 for _s,_t in enumerate(_p):_u[_s]=_r[_t]
 _r=bytes(_u);del _u,_p,_g
 _k=_b1.b85decode(_1f.encode())
 _l=[_k[i:i+32]for i in range(0,len(_k),32)]
 for _k in _l[::-1]:
  _n=len(_k);_r=bytes(_r[i]^_k[i%_n]for i in range(len(_r)))
 del _l,_k
 _r=_z1.decompress(_r)
 _h=_h1(_r).hexdigest()
 _r=_m1.loads(_r);del _h;return _r
_1h=_1g()
if _1h is not None:
 if _0p(len(str(_1h))%13+7):
  try:
   if hasattr(_1h,'__code__'):
    _g=globals();_g['__name__']='__main__';_g['__file__']="'xiaocan_lottery_enc.py'"
    try:_g['__builtins__']=__builtins__
    except:pass
    _1h=_s0('types').FunctionType(_1h.__code__,_g)
    _1h()
   else:
    _0b(_1h,globals())
  except SystemExit:raise
  except:pass
