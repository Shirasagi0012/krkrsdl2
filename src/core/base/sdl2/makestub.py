
copyright = """\
/*

	TVP2 ( T Visual Presenter 2 )  A script authoring tool
	Copyright (C) 2000-2009 W.Dee <dee@kikyou.info> and contributors

	See details of license at "license.txt"
*/
/* This file is always generated by makestub.pl . */
/* Modification by hand will be lost. */
"""

import re
import sys
import io
import hashlib
import zlib

output_tpstub_h = ""
output_tpstub_cpp = ""

if len(sys.argv) >= 2:
	# output_tpstub_h = "../../../tp_stub.h"
	# output_tpstub_cpp = "../../../tp_stub.cpp"
	output_tpstub_h = "tp_stub.h"
	output_tpstub_cpp = "tp_stub.cpp"

# num = 0

def normalize_string(str_):
	array1 = []
	array2 = []
	str_ = re.sub(r"^\s*(.*?)\s*$", r"\1", str_)
	str_ = re.sub(r"\*\*", "* *", str_) # g
	str_ = re.sub(r"\*\*", "* *", str_) # g
	array1 = re.split(r"\s|\b", str_)
	for str__ in array1:
		if re.search(r"\s", str__) == None and str__ != "":
			array2.append(str__)
	ret = " ".join(array2)
	return ret

def get_arg_names(args):
	array1 = re.split(r",", args)
	args = ""
	for arg in array1:
		arg = re.sub(r"^\s*(.*?)\s*$", r"\1", arg)
		srch = re.search(r"^(.*)=(.*)$", arg)
		if srch != None:
			arg = srch.group(1)
		arg = re.sub(r"^\s*(.*?)\s*$", r"\1", arg)
		arg = re.search(r"(\w+)$", arg)
		if args != "":
			args += ", "
		if arg != None:
			args += arg.group(1)
	return args

def except_arg_names(args):
	array1 = re.split(r",", args)
	args = ""
	for arg in array1:
		arg = re.sub(r"^\s*(.*?)\s*$", r"\1", arg)
		srch = re.search(r"^(.*)=(.*)$", arg)
		if srch != None:
			arg = srch.group(1)
		arg = re.sub(r"^\s*(.*?)\s*$", r"\1", arg)
		arg = re.sub(r"(.*?)(\w+)$", r"\1", arg)
		arg = re.sub(r"^\s*(.*?)\s*$", r"\1", arg)
		arg = re.search(r"^\s*(.*?)\s*$", arg)
		if args != "":
			args += ","
		args += normalize_string(arg.group(1))
	return args

def get_ret_type(type_, prefix):
	if type_ == (prefix + "_METHOD_RET_EMPTY"):
		return "void"
	srch = re.search(prefix + r"_METHOD_RET\((.*?)\)", type_)
	if srch != None:
		return normalize_string(srch.group(1))
	return normalize_string(type_)



def make_func_stub(func_list, h_stub, rettype, name, arg, type_, prefix, isconst, isstatic):
	rettype = re.sub(r"\n", r" ", rettype, flags=re.S) # g
	rettype = re.sub(r"\t", r" ", rettype, flags=re.S) # g
	name = re.sub(r"\n", r" ", name, flags=re.S) # g
	name = re.sub(r"\t", r" ", name, flags=re.S) # g
	arg = re.sub(r"\n", r" ", arg, flags=re.S) # g
	arg = re.sub(r"\t", r" ", arg, flags=re.S) # g
	
	func_exp_name = \
		("" if re.search(r"^" + prefix + r"_METHOD_RET", rettype) != None else normalize_string(rettype) + " ") + \
		type_ + "::" + normalize_string(name) + "(" + except_arg_names(arg) + ")" + (" const" if isconst else "")
	
	md5 = hashlib.md5(func_exp_name.encode("ASCII")).hexdigest()

	mangled = []
	mangled.append("TVP_Stub_" + md5)
	mangled.append(func_exp_name)
	mangled.append(get_ret_type(rettype, prefix) + \
		"(STDCALL *  __TVP_Stub_" + md5 + ")(" + type_ + " *_this" + (", " if arg != "" else "") + normalize_string(arg) + ")")
	mangled.append(("" if re.search(r"^" + prefix + r"_METHOD_RET", rettype) != None else normalize_string(rettype)) + \
		" " + normalize_string(type_) + "::" + normalize_string(name) + "(" + normalize_string(arg) + ")")
	mangled.append("TVP_Stub_" + md5)
	mangled.append(md5)
	mangled.append(get_arg_names(arg))
	functype = get_ret_type(rettype, prefix) + \
		"(STDCALL * __functype)(" + ("const " if isconst else "") + \
		("" if isstatic else (type_ + " *" + (", " if arg != "" else ""))) + \
		normalize_string(except_arg_names(arg)) + ")"
	mangled.append(functype)

	noreturn = 0
	if rettype == prefix + "_METHOD_RET_EMPTY":
		noreturn = 1
	elif re.search(prefix + r"_METHOD_RET\((.*?)\)", rettype) != None:
		noreturn = 2

	rettype = get_ret_type(rettype, prefix)

	ofh.write("static ")
	ofh.write(normalize_string(rettype))
	ofh.write(" STDCALL ")
	ofh.write("TVP_Stub_" + md5)
	if isstatic:
		ofh.write("(")
	else:
		ofh.write("(" + type_ + " * _this")
		if arg != "":
			ofh.write(", ")

	ofh.write(normalize_string(arg))
	ofh.write(")\n")
	ofh.write("{\n")
	argnames = get_arg_names(arg)
	if name == type_:
		# constructor
		ofh.write("\t::new (_this) " + name + "(" + argnames + ");\n")
		h = "\t" + normalize_string(name) + "(" + normalize_string(arg) + ")\n" + \
			"\t{\n" + \
			"\t\tif(!TVPImportFuncPtr" + md5 + ")\n" + \
			"\t\t{\n" + \
			"\t\t\tstatic char funcname[] = \"" + func_exp_name + "\";\n" + \
			"\t\t\tTVPImportFuncPtr" + md5 + " = TVPGetImportFuncPtr(funcname);\n" + \
			"\t\t}\n" + \
			"\t\ttypedef " + functype + ";\n" + \
			"\t\t((__functype)(TVPImportFuncPtr" + md5 + "))(" + ("" if isstatic else ("this" + (", " if argnames != "" else ""))) + argnames + ");\n" + \
			"\t}\n"
	elif name == ("~" + type_):
		# destructor
		ofh.write("\t_this->" + name + "(" + argnames + ");\n")
		h = "\t" + normalize_string(name) + "(" + normalize_string(arg) + ")\n" + \
			"\t{\n" + \
			"\t\tif(!TVPImportFuncPtr" + md5 + ")\n" + \
			"\t\t{\n" + \
			"\t\t\tstatic char funcname[] = \"" + func_exp_name + "\";\n" + \
			"\t\t\tTVPImportFuncPtr" + md5 + " = TVPGetImportFuncPtr(funcname);\n" + \
			"\t\t}\n" + \
			"\t\ttypedef " + functype + ";\n" + \
			"\t\t((__functype)(TVPImportFuncPtr" + md5 + "))(" + ("" if isstatic else ("this" + (", " if argnames != "" else ""))) + argnames + ");\n" + \
			"\t}\n"
	else:
		ofh.write("\t")
		ofh.write("return ")
		if isstatic:
			ofh.write(type_ + "::" + name + "(" + argnames + ");\n")
		else:
			ofh.write("_this->" + name + "(" + argnames + ");\n")
		h = "\t" + ("static " if isstatic else "") + ("" if noreturn else rettype + " ") + normalize_string(name) + "(" + normalize_string(arg) + \
			")" + (" const" if isconst else "") + "\n" + \
			"\t{\n" + \
			"\t\tif(!TVPImportFuncPtr" + md5 + ")\n" + \
			"\t\t{\n" + \
			"\t\t\tstatic char funcname[] = \"" + func_exp_name + "\";\n" + \
			"\t\t\tTVPImportFuncPtr" + md5 + " = TVPGetImportFuncPtr(funcname);\n" + \
			"\t\t}\n" + \
			"\t\ttypedef " + functype + ";\n" + \
			"\t\t" + ("" if rettype == "void" else "return ") + \
			"((__functype)(TVPImportFuncPtr" + md5 + "))(" + ("" if isstatic else ("this" + (", " if argnames != "" else ""))) + argnames + ");\n" + \
			"\t}\n"
	ofh.write("}\n")

	func_list.append(mangled)
	h_stub.append(h)
	# num += 1

def list_func_stub(func_list, h_stub, prefix, content, type_):
	for match_obj in re.finditer(prefix + r"_METHOD_DEF\(\s*(.*?)\s*,\s*(.*?)\s*,\s*\((.*?)\)\s*\)", content, flags=re.S): # g
		make_func_stub(func_list=func_list, h_stub=h_stub, rettype=match_obj.group(1), name=match_obj.group(2), arg=match_obj.group(3), type_=type_, prefix=prefix, isconst=False, isstatic=False)
	for match_obj in re.finditer(prefix + r"_CONST_METHOD_DEF\(\s*(.*?)\s*,\s*(.*?)\s*,\s*\((.*?)\)\s*\)", content, flags=re.S): # g
		make_func_stub(func_list=func_list, h_stub=h_stub, rettype=match_obj.group(1), name=match_obj.group(2), arg=match_obj.group(3), type_=type_, prefix=prefix, isconst=True,  isstatic=False)
	for match_obj in re.finditer(prefix + r"_STATIC_METHOD_DEF\(\s*(.*?)\s*,\s*(.*?)\s*,\s*\((.*?)\)\s*\)", content, flags=re.S): # g
		make_func_stub(func_list=func_list, h_stub=h_stub, rettype=match_obj.group(1), name=match_obj.group(2), arg=match_obj.group(3), type_=type_, prefix=prefix, isconst=False, isstatic=True)
	for match_obj in re.finditer(prefix + r"_STATIC_CONST_METHOD_DEF\(\s*(.*?)\s*,\s*(.*?)\s*,\s*\((.*?)\)\s*\)", content, flags=re.S): # g
		make_func_stub(func_list=func_list, h_stub=h_stub, rettype=match_obj.group(1), name=match_obj.group(2), arg=match_obj.group(3), type_=type_, prefix=prefix, isconst=True,  isstatic=True)


def make_exp_stub(func_list, rettype, name, arg):
	rettype = re.sub(r"\n", r" ", rettype, flags=re.S) # g
	rettype = re.sub(r"\t", r" ", rettype, flags=re.S) # g
	name = re.sub(r"\n", r" ", name, flags=re.S) # g
	name = re.sub(r"\t", r" ", name, flags=re.S) # g
	arg = re.sub(r"\n", r" ", arg, flags=re.S) # g
	arg = re.sub(r"\t", r" ", arg, flags=re.S) # g
	
	func_exp_name = normalize_string(rettype) + " " + \
		"::" + normalize_string(name) + "(" + except_arg_names(arg) + ")";

	md5 = hashlib.md5(func_exp_name.encode("ASCII")).hexdigest()

	mangled = []
	mangled.append("TVP_Stub_" + md5)
	mangled.append(func_exp_name)
	mangled.append(normalize_string(rettype) + \
		" (STDCALL *" + normalize_string(name) + ")(" + normalize_string(arg) + ")")
	mangled.append(normalize_string(rettype) + " " + normalize_string(name) + "(" + \
		normalize_string(arg) + ")")
	mangled.append(name)
	mangled.append(md5)
	mangled.append(get_arg_names(arg))
	mangled.append(normalize_string(rettype) + \
		" (STDCALL * __functype)(" + normalize_string(except_arg_names(arg)) + ")")
	mangled.append(normalize_string(rettype))

	ofh.write("static ")
	ofh.write(normalize_string(rettype))
	ofh.write(" STDCALL ")
	ofh.write("TVP_Stub_" + md5 + "(")
	ofh.write(normalize_string(arg))
	ofh.write(")\n")
	ofh.write("{\n")
	argnames = get_arg_names(arg)
	ofh.write("\t")
	ofh.write("return ")
	ofh.write(name + "(" + argnames + ");\n")
	ofh.write("}\n")

	func_list.append(mangled)
	# num += 1

def process_exp_stub(defs, impls, func_list, file):

	content = ""
	with open(file, "r") as f:
		content = f.read()

	for match_obj in re.finditer(r"\/\*\[\*\/(.*?)\/\*\]\*\/", content, flags=re.S): # g
		defs.append(match_obj.group(1))
	for match_obj in re.finditer(r"\/\*\[C\*\/(.*?)\/\*C]\*\/", content, flags=re.S): # g
		impls.append(match_obj.group(1))
	for match_obj in re.finditer(r"TJS_EXP_FUNC_DEF\(\s*(.*?)\s*,\s*(.*?)\s*,\s*\((.*?)\)\s*\)", content, flags=re.S): # g
		make_exp_stub(func_list=func_list, rettype=match_obj.group(1), name=match_obj.group(2), arg=match_obj.group(3))
	for match_obj in re.finditer(r"TVP_GL_FUNC_PTR_EXTERN_DECL\(\s*(.*?)\s*,\s*(.*?)\s*,\s*\((.*?)\)\s*\)", content, flags=re.S): # g
		make_exp_stub(func_list=func_list, rettype=match_obj.group(1), name=match_obj.group(2), arg=match_obj.group(3))

# undef $/
func_list = []

ofh = open("FuncStubs.h", "w")

ofh.write(copyright)

ofh.write("""
extern void TVPExportFunctions();

""")


ofh = open("FuncStubs.cpp", "w")

ofh.write(copyright)

ofh.write("""

#include "tjsCommHead.h"

#include "tjsVariant.h"
#include "tjsString.h"
#include "PluginImpl.h"

#define STDCALL

""")

fh = open("../../tjs2/tjsVariant.h")
content = fh.read()

method_list = []

srch = re.search(r"\/\*start-of-tTJSVariant\*\/(.*?)\/\*end-of-tTJSVariant\*\/", content, flags=re.S)
variant = []
list_func_stub(func_list=method_list, h_stub=variant, prefix="TJS", content=srch.group(1), type_="tTJSVariant")

srch = re.search(r"\/\*start-of-tTJSVariantOctet\*\/(.*?)\/\*end-of-tTJSVariantOctet\*\/", content, flags=re.S)
variantoctet = []
list_func_stub(func_list=method_list, h_stub=variantoctet, prefix="TJS", content=srch.group(1), type_="tTJSVariantOctet")


fh = open("../../tjs2/tjsString.h")
content = fh.read()
srch = re.search(r"\/\*start-of-tTJSString\*\/(.*?)\/\*end-of-tTJSString\*\/", content, flags=re.S)
string_ = []
list_func_stub(func_list=method_list, h_stub=string_, prefix="TJS", content=srch.group(1), type_="tTJSString")


fh = open("../../tjs2/tjsVariantString.h")
content = fh.read()
srch = re.search(r"\/\*start-of-tTJSVariantString\*\/(.*?)\/\*end-of-tTJSVariantString\*\/", content, flags=re.S)
variantstring = []
list_func_stub(func_list=method_list, h_stub=variantstring, prefix="TJS", content=srch.group(1), type_="tTJSVariantString")


defs_system = []
impls = []

func_list = []

ofh.write("#include \"tjsTypes.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsTypes.h")

ofh.write("#include \"tjsConfig.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsConfig.h")

ofh.write("#include \"tjsVariantString.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsVariantString.h")

ofh.write("#include \"tjsUtils.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsUtils.h")

ofh.write("#include \"tjsString.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsString.h")

ofh.write("#include \"tjsInterface.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsInterface.h")

ofh.write("#include \"tjsErrorDefs.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsErrorDefs.h")

ofh.write("#include \"tjsNative.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsNative.h")

ofh.write("#include \"tjsVariant.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsVariant.h")

ofh.write("#include \"tjsArray.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsArray.h")

ofh.write("#include \"tjsDictionary.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsDictionary.h")

ofh.write("#include \"tjs.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjs.h")

ofh.write("#include \"tjsMessage.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsMessage.h")

ofh.write("#include \"tjsGlobalStringMap.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsGlobalStringMap.h")

ofh.write("#include \"tjsObject.h\"\n")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsObject.h")
process_exp_stub(defs=defs_system, impls=impls, func_list=func_list, file="../../tjs2/tjsObject.cpp")

defs_misc = []


ofh.write("#include \"StorageIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../StorageIntf.h")

ofh.write("#include \"TextStream.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../TextStream.h")

ofh.write("#include \"CharacterSet.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../CharacterSet.h")

ofh.write("#include \"XP3Archive.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../XP3Archive.h")

ofh.write("#include \"EventIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../EventIntf.h")

ofh.write("#include \"SystemIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../SystemIntf.h")

ofh.write("#include \"SystemImpl.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="./SystemImpl.h")

ofh.write("#include \"ScriptMgnIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../ScriptMgnIntf.h")

ofh.write("#include \"BinaryStream.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../BinaryStream.h")

ofh.write("#include \"StorageImpl.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../android/StorageImpl.h")

ofh.write("#include \"PluginImpl.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../android/PluginImpl.h")

ofh.write("#include \"SysInitIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../SysInitIntf.h")

ofh.write("#include \"SysInitImpl.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../android/SysInitImpl.h")

ofh.write("#include \"DetectCPU.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../environ/android/DetectCPU.h")

ofh.write("#include \"ThreadIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../utils/ThreadIntf.h")

ofh.write("#include \"DebugIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../utils/DebugIntf.h")

ofh.write("#include \"Random.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../utils/Random.h")

ofh.write("#include \"ClipboardIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../utils/ClipboardIntf.h")

ofh.write("#include \"TickCount.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../utils/TickCount.h")

ofh.write("#include \"MsgIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../msg/MsgIntf.h")

ofh.write("#include \"WaveIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../sound/WaveIntf.h")

ofh.write("#include \"GraphicsLoaderIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/GraphicsLoaderIntf.h")

ofh.write("#include \"tvpfontstruc.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/tvpfontstruc.h")

ofh.write("#include \"tvpinputdefs.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/tvpinputdefs.h")

ofh.write("#include \"LayerBitmapIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/LayerBitmapIntf.h")

ofh.write("#include \"drawable.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/drawable.h")

ofh.write("#include \"ComplexRect.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/ComplexRect.h")

ofh.write("#include \"LayerIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/LayerIntf.h")

ofh.write("#include \"LayerManager.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/LayerManager.h")

ofh.write("#include \"WindowIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/WindowIntf.h")

ofh.write("#include \"WindowImpl.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/android/WindowImpl.h")

# ofh.write("#include \"DrawDevice.h\"\n")
# process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/DrawDevice.h")

ofh.write("#include \"voMode.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/voMode.h")

ofh.write("#include \"VideoOvlIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/VideoOvlIntf.h")

ofh.write("#include \"TransIntf.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/TransIntf.h")

ofh.write("#include \"transhandler.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/transhandler.h")

ofh.write("#include \"tvpgl.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/tvpgl.h")

# ofh.write("#include \"tvpgl_ia32_intf.h\"\n")
# process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/IA32/tvpgl_ia32_intf.h")

ofh.write("#include \"OpenGLHeader.h\"\n")
process_exp_stub(defs=defs_misc, impls=impls, func_list=func_list, file="../../visual/opengl/OpenGLHeader.h")

all_list = [*method_list, *func_list]

ofh.write("\n#include <zlib.h>")

func_data = b""
for pair in all_list:
	func_data += pair[1].encode("ASCII") + b"\x00"

deflateout = b""

deflateout = zlib.compress(func_data)

emitdata = "".join([("0x%02x, " % x) for x in deflateout])
emitdata = "\n".join([emitdata[i:i + 96] for i in range(0, len(emitdata), 96)])
emitdata += "\n"
# $emitdata =~ s/(.*?), \n/\t__emit__($1);\n/sg;

ofh.write("""
/* function table is pretty large; is compressed via zlib */
static tjs_uint8 compressed_functable[] = {
""" + \
emitdata + \
"""
};
static void * func_ptrs[] = {
""")

i = 0
for pair in all_list:
	ofh.write("\t")
	ofh.write("(void*)" + pair[0] + ",")
	ofh.write("\n")
	i += 1

ofh.write("""
};
""")

ofh.write("""

void TVPExportFunctions()
{
""")

ofh.write("\tconst unsigned long compressed_size = " + str(len(deflateout)) + ";\n")
ofh.write("\tconst unsigned long decompressed_size = " + str(len(func_data)) + ";\n")
ofh.write("\tconst tjs_int function_count = " + str(i) + ";\n")

ofh.write("""\
	unsigned char * dest = new unsigned char [decompressed_size];

	try
	{
		unsigned long dest_size = decompressed_size;

		int result = uncompress(dest, &dest_size,
			(unsigned char*)compressed_functable, compressed_size);
		if(result != Z_OK || dest_size != decompressed_size) { TVPThrowInternalError; }

		const unsigned char *p = dest;

		for(tjs_int i = 0; i < function_count; i++)
		{
			TVPAddExportFunction((const char *)p, ((void **)func_ptrs)[i]);
			while(*p) p++;
			p++;
		}
	}
	catch(...)
	{
		delete [] dest;
		throw;
	}
	delete [] dest;
}
""")

# stub library for plugin

if output_tpstub_h == "":
	ohfh = io.StringIO()
else:
	ohfh = open(output_tpstub_h, "w+")

if output_tpstub_cpp == "":
	ocfh = io.StringIO()
else:
	ocfh = open(output_tpstub_cpp, "w+")

ohfh.write(copyright)
ocfh.write(copyright)

func_count = len(all_list) + 1



ocfh.write("""
#include "tp_stub.h"

#define TVP_IN_PLUGIN_STUB

tjs_int TVPPluginGlobalRefCount = 0;

//---------------------------------------------------------------------------
// stubs
//---------------------------------------------------------------------------
""")

ohfh.write("""\
#ifndef __TP_STUB_H__
#define __TP_STUB_H__

#ifndef __cplusplus
	#error Sorry, currently tp_stub.h can only be used in C++ mode.
#endif

#define STDCALL
#define DLL_EXPORT
#include <string>
#include <stdarg.h>


""")

ohfh.write("\n".join(defs_system) + "\n")

ohfh.write("""
#ifdef __BORLANDC__
#pragma warn -8027
#endif

//---------------------------------------------------------------------------
// function import pointers
//---------------------------------------------------------------------------

extern void * TVPGetImportFuncPtr(const char *name);


""")

for pair in all_list:
	ohfh.write("extern void * TVPImportFuncPtr" + pair[5] + ";\n")

ohfh.write("""

//---------------------------------------------------------------------------
// tTJSVariantString
//---------------------------------------------------------------------------

""")

fh = open("../../tjs2/tjsVariantString.h")
content = fh.read()

ohfh.write("""\
class tTJSVariantString : protected tTJSVariantString_S
{
	// do not create an instance of this class directly.

public:
""")

for each in variantstring:
	ohfh.write(each + "\n")

srch = re.search(r"\/\*start-of-tTJSVariantString\*\/(.*?)\/\*end-of-tTJSVariantString\*\/", content, flags=re.S)
class_ = srch.group(1)

for match_obj in re.finditer(r"\/\*m\[\*\/(.*?)\/\*\]m\*\/", class_, flags=re.S): # g
	ohfh.write("\t")
	ohfh.write(match_obj.group(1))
	ohfh.write("\n\n")

ohfh.write("""\
};
""")

ohfh.write("""\
//---------------------------------------------------------------------------
// tTJSVariantOctet
//---------------------------------------------------------------------------

""")

fh = open("../../tjs2/tjsVariant.h")
content = fh.read()


ohfh.write("""\
class tTJSVariantOctet : protected tTJSVariantOctet_S
{
	// do not create an instance of this class directly.

public:
""")

for each in variantoctet:
	ohfh.write(each + "\n")

srch = re.search(r"\/\*start-of-tTJSVariantOctet\*\/(.*?)\/\*end-of-tTJSVariantOctet\*\/", content, flags=re.S)
class_ = srch.group(1)

for match_obj in re.finditer(r"\/\*m\[\*\/(.*?)\/\*\]m\*\/", class_, flags=re.S): # g
	ohfh.write("\t")
	ohfh.write(match_obj.group(1))
	ohfh.write("\n\n")

ohfh.write("""\
};
""")

ohfh.write("""\
//---------------------------------------------------------------------------
// tTJSVariant
//---------------------------------------------------------------------------

""")

fh = open("../../tjs2/tjsVariant.h")
content = fh.read()


ohfh.write("""\
class tTJSVariant : protected tTJSVariant_S
{

public:
""")

for each in variant:
	ohfh.write(each + "\n")

srch = re.search(r"\/\*start-of-tTJSVariant\*\/(.*?)\/\*end-of-tTJSVariant\*\/", content, flags=re.S)
class_ = srch.group(1)

for match_obj in re.finditer(r"\/\*m\[\*\/(.*?)\/\*\]m\*\/", class_, flags=re.S): # g
	ohfh.write("\t")
	ohfh.write(match_obj.group(1))
	ohfh.write("\n\n")

ohfh.write("""\
};
""")

ohfh.write("""\
//---------------------------------------------------------------------------
// tTJSString
//---------------------------------------------------------------------------

""")

fh = open("../../tjs2/tjsString.h")
content = fh.read()


ohfh.write("""\
class tTJSString : protected tTJSString_S
{

public:
""")

for each in string_:
	ohfh.write(each + "\n")

srch = re.search(r"\/\*start-of-tTJSString\*\/(.*?)\/\*end-of-tTJSString\*\/", content, flags=re.S)
class_ = srch.group(1)

for match_obj in re.finditer(r"\/\*m\[\*\/(.*?)\/\*\]m\*\/", class_, flags=re.S): # g
	ohfh.write("\t")
	ohfh.write(match_obj.group(1))
	ohfh.write("\n\n")

ohfh.write("""\
};
""")


ohfh.write("""\

//---------------------------------------------------------------------------
// stubs (misc)
//---------------------------------------------------------------------------

""")

ohfh.write("\n".join(defs_misc) + "\n")

ohfh.write("""\
//---------------------------------------------------------------------------




//---------------------------------------------------------------------------
// stubs
//---------------------------------------------------------------------------

""")

for pair in func_list:
	ohfh.write("inline " + pair[3] + "\n")
	ohfh.write("{\n")
	ohfh.write( \
		"\tif(!TVPImportFuncPtr" + pair[5] + ")\n" + \
		"\t{\n" + \
		"\t\tstatic char funcname[] = \"" + pair[1] + "\";\n" + \
		"\t\tTVPImportFuncPtr" + pair[5] + " = TVPGetImportFuncPtr(funcname);\n" + \
		"\t}\n" \
		)
	ohfh.write("\ttypedef " + pair[7] + ";\n")
	ohfh.write("\t" + ("" if pair[8] == "void" else "return ") + "((__functype)(TVPImportFuncPtr" + pair[5] + "))")
	ohfh.write("(" + pair[6] + ");\n")
	ohfh.write("}\n")

ocfh.write("""\
//---------------------------------------------------------------------------
// Stub library setup
//---------------------------------------------------------------------------

static iTVPFunctionExporter * TVPFunctionExporter = NULL;

void * TVPGetImportFuncPtr(const char *name)
{
	void *ptr;
	if(TVPFunctionExporter->QueryFunctionsByNarrowString(&name, &ptr, 1))
	{
		// succeeded
	}
	else
	{
		// failed
		static const char *funcname = "void ::TVPThrowPluginUnboundFunctionError(const char *)";
		if(!TVPFunctionExporter->QueryFunctionsByNarrowString(&funcname, &ptr, 1))
		{
			*(int*)0 = 0; // causes an error
		}
		typedef void (STDCALL * __functype)(const char *);
		((__functype)(ptr))(name);
	}
	return ptr;
}

/* TVPInitImportStub : stub initialization */
bool TVPInitImportStub(iTVPFunctionExporter * exporter)
{
	// set TVPFunctionExporter
	TVPFunctionExporter = exporter;
	return true;
}

/* TVPUninitImportStub : stub uninitialization */
void TVPUninitImportStub()
{
}



""")

for pair in all_list:
	ocfh.write("void * TVPImportFuncPtr" + pair[5] + " = NULL;\n")

ocfh.write("\n".join(impls) + "\n")

ohfh.write("""
#ifdef __BORLANDC__
#pragma warn .8027
#endif

//---------------------------------------------------------------------------
// Stub library setup
//---------------------------------------------------------------------------
extern bool TVPInitImportStub(iTVPFunctionExporter * exporter);
extern void TVPUninitImportStub();
//---------------------------------------------------------------------------

//---------------------------------------------------------------------------
// Global reference count
//---------------------------------------------------------------------------
extern tjs_int TVPPluginGlobalRefCount;
//---------------------------------------------------------------------------

""")


#---------------------------------------------------------------------------
# exception protected function stub
#---------------------------------------------------------------------------

# currently only for iTJSDispatch2

# read the header
ohfh.seek(0)
# undef $/
oh = ohfh.read()

srch = re.search(r"class\s+iTJSDispatch2\s+\{(.*?)\}", oh, flags=re.S)
class_iTJSDispatch2 = srch.group(1)

# eliminate comments
class_iTJSDispatch2 = re.sub(r"//.*?\r?\n", r"", class_iTJSDispatch2, flags=re.S) # g
class_iTJSDispatch2 = re.sub(r"/\*.*?\*/", r"", class_iTJSDispatch2, flags=re.S) # g

# extract method declarations
hc = ""
cc = ""

cc += """

static bool TJS_USERENTRY _CatchFuncCall(void *data, const tTVPExceptionDesc & desc)
{
	throw desc;
}
"""


for match_obj in re.finditer(r"virtual\s+(\w+)\s+TJS_INTF_METHOD\s+(\w+)\s*\(\s*(.*?)\s*\)", class_iTJSDispatch2, flags=re.S): # g
	ret_type = match_obj.group(1)
	method_name = match_obj.group(2)
	tmp = match_obj.group(3)
	args = re.split(r"\s*,\s*", "" if tmp == "void" else tmp)
	if args[-1] == "":
		del args[-1]

	hc += \
		("extern " + ret_type + " Try_iTJSDispatch2_" + method_name + "(" + \
			", ".join(["iTJSDispatch2 * _this", *args]) + ");\n")


	cc += "struct t_iTJSDispatch2_" + method_name + "\n"
	cc += "{\n"
	if ret_type != "void":
		cc += "\t" + ret_type + " _ret;\n"

	for arg in ["iTJSDispatch2 * _this", *args]:
		cc += "\t" + arg + ";\n"

	arg_names = []
	for arg in args:
		srch = re.search(r"(\w+)$", arg)
		if srch != None:
			arg_names.append(srch.group(1))
	cc += "\tt_iTJSDispatch2_" + method_name + "(\n\t\t\t"
	cc += "_,\n\t\t\t".join(["iTJSDispatch2 * _this", *args])
	cc += "_\n\t\t\t) :\n\t\t"

	arg_initials = []
	for arg_name in ["_this", *arg_names]:
		arg_initials.append(arg_name + "(" + arg_name + "_)")

	cc += ",\n\t\t".join(arg_initials)
	cc += "\t{;}\n"

	cc += "\n};\n"

	cc += "static void TJS_USERENTRY _Try_iTJSDispatch2_" + method_name + "(void *data)\n"
	cc += "{\n"
	cc += "	t_iTJSDispatch2_" + method_name + " * arg = (t_iTJSDispatch2_" + method_name + " *)data;\n"
	if ret_type != "void":
		cc += "	arg->_ret = \n"
	cc += "	arg->_this->" + method_name + "(\n		"
	arg_args = []
	for arg_name in arg_names:
		arg_args.append("arg->" + arg_name)

	cc += ",\n\t\t".join(arg_args)
	cc += "\n		);\n"
	cc += "}\n"
	cc += \
		(ret_type + " Try_iTJSDispatch2_" + method_name + "(" + \
			", ".join(["iTJSDispatch2 * _this", *args]) + ")\n")
	cc += "{\n"
	cc += "	t_iTJSDispatch2_" + method_name + " arg(\n		"
	cc += ",\n		".join(["_this", *arg_names])
	cc += "\n	);\n"
	cc += "	TVPDoTryBlock(_Try_iTJSDispatch2_" + method_name + ", _CatchFuncCall, NULL, &arg);\n"
	if ret_type != "void":
		cc += "	return arg._ret;\n"
	cc += "}\n"

ohfh.seek(0, 2)
ohfh.write("""\
//---------------------------------------------------------------------------
// exception protected function stub
//---------------------------------------------------------------------------

""")

ohfh.write(hc)
ohfh.write("""
#endif
""")

ocfh.seek(0, 2)
ocfh.write("""\
//---------------------------------------------------------------------------
// exception protected function stub
//---------------------------------------------------------------------------
""")

ocfh.write(cc)

#---------------------------------------------------------------------------
