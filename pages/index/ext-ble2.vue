<template>

	<div>
		<div>
			<text>BLE蓝牙相关接口</text>
		</div>
		<!-- split line -->
		<view style="border-bottom: 1px solid #ccc; margin: 10px 0;"></view>
		<!-- a list to display scan_result -->
		<view style="width: 100%; overflow-x: auto;">
			<text v-for="(item, index) in scan_result" :key="index" style="display: block; border-bottom: 1px solid #ccc; padding: 5px 0; white-space: normal;" @click="handleItemClick(item)">
				{{JSON.stringify(item)}}
			</text>
		</view>
		<div>
			<!-- heartbeat status, data length received -->
			<text>心跳状态: {{heartbeatInterval ? '开启' : '关闭'}} {{heartbeatStatusIcon}}</text>
			<text>数据长度: {{pcmDataReceived}}</text>
		</div>
		<button type="primary" @click="microphoneRecording">麦克风录音完整流程</button>
		<button type="primary" @click="initBleSDK">初始化</button>
		<button type="primary" @click="isBlueEnable">蓝牙是否开启</button>
		<button type="primary" @click="enableBluetooth">打开蓝牙</button>
		<button type="primary" @click="disableBluetooth">关闭蓝牙</button>
		<button type="primary" @click="startScan">开始扫描</button>
		<button type="primary" @click="stopScan">停止扫描</button>
		<button type="primary" @click="connect">连接</button>
		<button type="primary" @click="disconnect">断开连接</button>
		<button type="primary" @click="startHeartBeat">开启定时心跳</button>
		<button type="primary" @click="stopHeartBeat">关闭定时心跳</button>
		<button type="primary" @click="startOTA">开始OTA</button>
		<button type="primary" @click="cancelOTA">取消OTA</button>
		<button type="primary" @click="startCallingRecord">开始通话录音</button>
		<button type="primary" @click="stopCallingRecord">结束录音</button>
		<button type="primary" @click="startMicrophoneRecord">开始麦克风录音</button>
		<button type="primary" @click="sendTestData2">发送心跳</button>
		<button type="primary" @click="registerDataCallback">注册监听器</button>
		<button type="primary" @click="unRegisterDataCallback">取消注册监听器</button>
		<button type="primary" @click="decoderOpus">解码opus</button>
		<button type="primary" @click="textToRawPcm">文本文件转二进制 Pcm</button>
		<button type="primary" @click="splitChannels">分离左右声道</button>
		<button type="primary" @click="denoisePcmFile">Pcm 文件降噪</button>
		<button type="primary" @click="waveToPcm">Wav to Pcm</button>
		<button type="primary" @click="pcmToWav">Pcm to Wav</button>
		<button type="primary" @click="splitChannelsTest">分离左右声道测试</button>
		<button type="primary" @click="classicalRecord">系统通道录音</button>
		<button type="primary" @click="stopClassicalRecord">停止系统通道录音</button>
		<button type="primary" @click="requestAudioRecordPermission">请求录音权限</button>
		<button type="primary" @click="startNativeRecord">开始原生录音</button>
		<button type="primary" @click="stopNativeRecord">结束原生录音</button>
		<button type="primary" @click="classicalRecordDenoise">系统通道录音降噪</button>
		<button type="primary" @click="exportFile">导出文本录音文件</button>
		<button type="primary" @click="exportPcmFile">导出二进制PCM录音文件</button>
		<button type="primary" @click="exportPcmLeftFile">导出声道0二进制PCM录音文件</button>
		<button type="primary" @click="exportPcmRightFile">导出声道1二进制PCM录音文件</button>
		<button type="primary" @click="exportPcmLeftDenoiseFile">导出声道0二进制PCM降噪文件</button>
		<button type="primary" @click="exportPcmRightDenoiseFile">导出声道1二进制PCM降噪文件</button>
	</div>
</template>

<script>
	//必须引入的Recorder核心（文件路径是 /src/recorder-core.js 下同），使用import、require都行
	import Recorder from 'recorder-core' //注意如果未引用Recorder变量，可能编译时会被优化删除（如vue3 tree-shaking），请改成 import 'recorder-core'，或随便调用一下 Recorder.a=1 保证强引用

	import 'recorder-core/src/engine/pcm.js'

	//必须引入的RecordApp核心文件（文件路径是 /src/app-support/app.js）
	import RecordApp from 'recorder-core/src/app-support/app'

	//所有平台必须引入的uni-app支持文件（如果编译出现路径错误，请把@换成 ../../ 这种）
	import '@/uni_modules/Recorder-UniCore/app-uni-support.js'
	
	// 获取 module 
	var sdkModule = uni.requireNativePlugin("XM-BesAllModule")
	// var testModule = uni.requireNativePlugin("TestModule")
	var deviceProtocol = 1 // 1:BLE, 16:SPP
	// const modal = uni.requireNativePlugin('modal');
	// 是否在录音
	var isRecording = false
	var filenameStub = 'plugin-demo-pcm'
	///
	/// 测试文件命名规则：
	/// 
	/// 坑：uniapp 不能写二进制文件，只能写字符串文件，所以录音原始数据先转成字符串保存。
	///
	/// 1. filenameStub + '.pcm'：录音原始数据，字符串格式，逗号分隔
	/// 2. filenameStub + '-left.pcm': 左声道数据，字符串格式，逗号分隔
	/// 3. filenameStub + '-right.pcm': 右声道数据，字符串格式，逗号分隔
	/// 4. filenameStub + '-left-raw.pcm': 左声道数据，二进制格式
	/// 5. filenameStub + '-right-raw.pcm': 右声道数据，二进制格式
	/// 7. filenameStub + '-left-raw-denoise.pcm': 左声道数据，二进制格式，降噪后
	/// 8. filenameStub + '-right-raw-denoise.pcm': 右声道数据，二进制格式，降噪后
	///

	// char 数据，保存录音
	var pcmData = []
	var Build = plus.android.importClass("android.os.Build");
	var Manifest = plus.android.importClass("android.Manifest");
	var MainActivity = plus.android.runtimeMainActivity();
	export default {
		mounted() {
			RecordApp.UniRenderjsRegister(this);
		},
		data() {
			return {
				// address: "94F206C6-42EE-8395-3CE1-3A8F15FA57FD"
				// address: "EE:11:22:33:C1:79"//By Macro
				address: "EE:11:22:33:3D:78", // tz test device ble address
				classicalAddress: "11:11:22:33:3D:78", // tz test device classical address
				iosBleAddress: "A69C430A-92A5-CEDD-FFE1-B7958A028711", // tz test device ios ble address
				// address: "EE:11:22:33:BF:84", // tz xl test device ble address
				// classicalAddress: "11:11:22:33:BF:84" // tz xl test device classical address
				pcmDataReceived: 0,
				heartbeatInterval: null,
				heartbeatStatusIcon: '❌',
				scan_result: [],
				saved_text_filepath: ''
			}
		},
		onLoad() {
			Recorder.a = 1
		},
		methods: {
			uniPage__onShow(){ //页面onShow时【必须调用】的函数，传入当前组件this
				RecordApp.UniPageOnShow(this);
			},
			toast(message) {
				plus.nativeUI.toast(message);
			},
			deleteAFile(filename, callback) {
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', { create: true }, (dirEntry) => {
						dirEntry.getFile(filename, {
							create: true
						}, (fileEntry) => {
							fileEntry.remove((entry) => {
								console.log('remove success', entry);
								if (callback) {
									callback();
								}
							}, (e) => {
								console.log('remove error', e);
							});
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			getAFilePath(filename, callback) {
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', { create: true }, (dirEntry) => {
						dirEntry.getFile(filename, {
							create: true
						}, (fileEntry) => {
							if (callback) {
								callback(fileEntry.fullPath);
							}
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			handleItemClick(item) {
				console.log('handleItemClick', item);
				// this.toast(JSON.stringify(item));
				// set macAddress
				// iOS
				if (plus.os.name === 'iOS') {
					this.iosBleAddress = item.bleAddress;
					this.toast('iOS ble address: ' + this.iosBleAddress);
				} else {
					// Android
					this.address = "";
					// SPP 模式下，scan 的结果没有 bleAddress，只有 deviceMAC
					// 这里把 deviceMAC 作为 address，是为了避开 connect 接口的校验，
					// 没有实际意义
					if (item.bleAddress) {
						this.address = item.bleAddress;
					}
					if (item.deviceMAC) {
						this.address = item.deviceMAC;
					}
					// spp mac address
					this.classicalAddress = item.deviceMAC;
					this.toast('Android ble address: ' + this.address + ' spp mac address: ' + this.classicalAddress);
				}
			},
			classicalRecord() {
				var that = this;
				// 删除录音文件
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
						dirEntry.getFile(filenameStub + '-sys.pcm', {
							create: true
						}, (fileEntry) => {
							fileEntry.remove((entry) => {
								console.log('remove success', entry);
								// 重新创建文件
								dirEntry.getFile(filenameStub + '-sys.pcm', {
									create: true
								}, (fileEntry) => {
									// path of fileEntry
									console.log('fileEntry', fileEntry.fullPath);

									// 开始录音
									that.doClassicalRecord();
								}, (e) => {
									console.log('getFile error', e);
								})
							}, (e) => {
								console.log('remove error', e);
							});
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			doClassicalRecord() {
				RecordApp.UniWebViewActivate(this); //App环境下必须先切换成当前页面WebView
				RecordApp.RequestPermission(()=>{
					console.log("已获得录音权限，可以开始录音了");

					pcmData = []

					RecordApp.UniWebViewActivate(this);
					RecordApp.Start({
						type: 'pcm',
						sampleRate: 16000,
						bitRate: 16,
						audioTrackSet: {
							noiseSuppression: false, echoCancellation: false, autoGainControl: false
						},
						onProcess: (buffers, powerLevel, duration, sampleRate, newBufferIdx, asyncEnd) => {
							console.log("buffers", buffers[0].length, "powerLevel", powerLevel, "duration", duration, "sampleRate", sampleRate, "newBufferIdx", newBufferIdx);
							// console.log("buffers", buffers);
							// buffers 是一个数组，数组长度为 1。buffers[0] 是一个 dict，这里用一个 dict 来表示一个 buffer，index 是 buffer 的序号，data 是 buffer 的数据，数据类型 unsigned short
							// [{"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0,"24":0,"25":0,"26":0,"27":0,"28":0,"29":0,"30":0,"31":0,"32":0,"33":0,"34":0,"35":0,"36":0,"37":0,"38":0,"39":0,"40":0,"41":0}]
							// 把 buffers 转化为 Uint8Array
							var bufferDict = buffers[0];
							var bufferArray = [];
							for (var key in bufferDict) {
								// console.log("key", key);
								bufferArray.push(bufferDict[key]);
							}
							// var buffer = new Uint16Array(bufferArray);
							pcmData.push(...bufferArray);
							// json options
							// var options = {
							// 	pcmData: bufferDict,
							// 	sampleRate: sampleRate
							// }
							// var denoised = sdkModule.denoisePcmBufferEx(options);
							// console.log("denoised success", denoised.success, "data len", denoised.data.length);
							// if (denoised.success) {
							// 	pcmData.push(...denoised.data);
							// }
						},
					})
				},(msg,isUserNotAllow)=>{
					if(isUserNotAllow){//用户拒绝了录音权限
						//这里你应当编写代码进行引导用户给录音权限，不同平台分别进行编写
					}
					console.error("请求录音权限失败："+msg);
				});
			},
			stopClassicalRecord() {
				RecordApp.Stop(null, (msg) => {
					console.log("录音结束", msg);

					// 添加 denoised.data 到文件 filepath
					plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
						dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
							dirEntry.getFile(filenameStub + '-sys.pcm', {
								create: true
							}, (fileEntry) => {
								fileEntry.createWriter((writer) => {
									writer.onwrite = function(e) {
										console.log('write success', e);
									};
									writer.onerror = function(e) {
										console.log('write error', e);
									};
									console.log('write ' + pcmData.length);
									writer.write(pcmData.toString());
								}, (e) => {
									console.log('createWriter error', e);
								});
							}, (e) => {
								console.log('getFile error', e);
							})
						}, (e) => {
							console.log('getDirectory error', e);
						})
					}, (e) => {
						console.log('requestFileSystem error', e);
					});
				})
			},
			requestPermissionAndroid(permission) {
				if (Build.VERSION.SDK_INT >= 23) {
					if (MainActivity.checkSelfPermission(permission) == -1) {
						// Request the permission
						MainActivity.requestPermissions([permission], 1);
						
						// Optional: Add permission result callback
						plus.globalEvent.addEventListener('onRequestPermissionsResult', (e) => {
							if (e.requestCode == 1) { // Match the request code we used
								if (e.grantResults[0] == 0) { // Permission granted
									this.toast("Permission granted");
								} else {
									this.toast("Permission denied");
								}
							}
						});
						
						return false;
					}
				}
				return true;
			},
			requestAudioPermissionIos() {
				// Import required iOS classes
				var AVAudioSession = plus.ios.importClass("AVAudioSession");
				var session = AVAudioSession.sharedInstance();
				
				// Request recording permission
				session.requestRecordPermission((granted) => {
					if (granted) {
						this.toast("Recording permission granted");
					} else {
						this.toast("Recording permission denied");
						
						// Open app settings if permission denied
						var NSURL = plus.ios.importClass('NSURL');
						var UIApplication = plus.ios.importClass('UIApplication');
						
						var settingsUrl = NSURL.URLWithString('app-settings:');
						var application = UIApplication.sharedApplication();
						
						if (application.canOpenURL(settingsUrl)) {
							application.openURL(settingsUrl);
						}
					}
				});
			},
			requestAudioRecordPermission() {
				if (plus.os.name === 'iOS') {
					this.requestAudioPermissionIos();
				} else {
					this.requestPermissionAndroid(Manifest.permission.RECORD_AUDIO);
				}
			},
			startNativeRecord() {
				this.requestAudioRecordPermission();

				var that = this;
				this.deleteAFile(filenameStub + '-sys-raw.pcm', () => {
					that.deleteAFile(filenameStub + '-sys-raw-denoise.pcm', () => {
						plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
							that.getAFilePath(filenameStub + '-sys-raw.pcm', (fullPath) => {
								var denoiseFilepath = fullPath.replace('-raw.pcm', '-raw-denoise.pcm');
								sdkModule.startAudioRecord({
									pcmPath: fullPath // 调试用，如果传入 ""，则不保存文件
								}, (ret) => {
									console.log('startAudioRecord', ret.msg)
									if (ret.data && ret.data.length > 0) {
										console.log('startAudioRecord', ret.data.length)
										// console.log('startAudioRecord', ret.data)
										// convert to Uint8Array
										// var buffer = new Uint8Array(ret.data);
										// console.log('startAudioRecord', buffer.length)
										var denoiseResult = sdkModule.denoisePcmBufferEx({
											sampleRate: 16000,
											pcmData: ret.data,
											pcmPath: denoiseFilepath // 调试用，如果传入 ""，则不保存文件
										})
										console.log('denoisePcmBufferEx', denoiseResult.success, denoiseResult.data.length)
									}
								})
							})
						})
					})
				})
			},
			stopNativeRecord() {
				sdkModule.stopAudioRecord((ret) => {
					console.log('stopAudioRecord', ret.msg)
					// toast
					this.toast(ret.msg);
				})
			},
			classicalRecordDenoise() {
			},
			exportFile() {
				this.doExportFile(filenameStub + '.pcm');
			},
			exportPcmFile() {
				this.doExportFile(filenameStub + '-raw.pcm');
			},
			exportPcmLeftFile() {
				this.doExportFile(filenameStub + '-left-raw.pcm');
			},
			exportPcmRightFile() {
				this.doExportFile(filenameStub + '-right-raw.pcm');
			},
			exportPcmLeftDenoiseFile() {
				this.doExportFile(filenameStub + '-left-raw-denoise.pcm');
			},
			exportPcmRightDenoiseFile() {
				this.doExportFile(filenameStub + '-right-raw-denoise.pcm');
			},
			doExportFile(filename) {
				var that = this;
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
						dirEntry.getFile(filename, {
							create: true
						}, (fileEntry) => {
							// path of fileEntry
							console.log('fileEntry', fileEntry.fullPath);
							// that.exportFile(fileEntry.fullPath)
							if (plus.os.name === 'iOS') {
								uni.openDocument({
									filePath: fileEntry.fullPath,
									fileType: 'wav',
									success: function(res) {
										console.log('open document success');
									},
									fail: function(err) {
										console.log('open document fail', err);
									}
								})
							} 
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			// export file
			exportFilePath(filepath) {
				console.log('exportFile', filepath);
				// if the OS is iOS, use UIActivityViewController to share the file
				if (plus.os.name === 'iOS') {
					var UIActivityViewController = plus.ios.importClass('UIActivityViewController');
					var NSURL = plus.ios.importClass('NSURL');

					var url = NSURL.fileURLWithPath(filepath, false);
					var activityItems = UIActivityViewController.alloc().initWithActivityItems([url], null);
					var app = plus.ios.invoke('UIApplication', 'sharedApplication');
					var window = app.keyWindow;
					var rootViewController = window.rootViewController;
					rootViewController.presentViewController(activityItems, true, null);
				} else {
					// if the OS is Android, use Intent.ACTION_SEND to share the file
					var Intent = plus.android.importClass('android.content.Intent');
					var Uri = plus.android.importClass('android.net.Uri');
					var File = plus.android.importClass('java.io.File');
					var intent = new Intent();
					intent.setAction(Intent.ACTION_SEND);
					var uri = Uri.fromFile(new File(filepath));
					intent.putExtra(Intent.EXTRA_STREAM, uri);
					intent.setType('*/*');
					plus.android.runtimeMainActivity().startActivity(Intent.createChooser(intent, 'Share'));
				}
			},
			getMacAddress() {
				var platform = uni.getSystemInfoSync().platform;
				// Android
				if (platform === 'android') {
					return this.address;
				} else if (platform === 'ios') {
					// iOS
					return this.iosBleAddress; // tz test device ios ble address
				}
			},
			microphoneRecording() {
				// 1. 初始化
				sdkModule.init({
					enableDenoise: true
				}, (ret) => {
					console.log('init', ret);

					// 如果是 iOS 平台，deviceProtocol 设置为 1
					// 如果是 Android 平台，deviceProtocol 设置为 16。Android 平台上 1 也能工作。
					var platform = uni.getSystemInfoSync().platform;
					if (platform === 'android') {
						deviceProtocol = 16;
					} else if (platform === 'ios') {
						deviceProtocol = 1;
					}

					//不需要设置的参数请注释掉
					sdkModule.initBleSDK({
						deviceProtocol: deviceProtocol // 1:BLE, 16:SPP，初始化后不能随便修改
					}, (ret) => {
						//扫描回调结果
						console.log(ret)
						this.toast(JSON.stringify(ret));
						// 1.5 断开连接
						sdkModule.disconnect((ret) => {
							console.log('disconnect', ret);
							this.toast(JSON.stringify(ret));
							// 2. 连接设备
							sdkModule.connect({
								macAddress: this.getMacAddress(),
								deviceMac: this.classicalAddress
							}, (ret) => {
								console.log("connect", ret)
								this.toast(JSON.stringify(ret));

								// 2.5 unregister callback
								sdkModule.unRegisterDataCallback();

								// 3. 注册回调
								sdkModule.registerDataCallback((ret) => {
									console.log('callback', ret)
									// this.toast(JSON.stringify(ret));
									// if ret.data is "5bb500", it's a heartbeat response
									if (ret.data === '5bb500') {
										if (this.heartbeatStatusIcon === '✅') {
											this.heartbeatStatusIcon = '❌'
										} else {
											this.heartbeatStatusIcon = '✅'
										}
									}
								});

								// 4. 开启定时心跳
								sdkModule.startSendBLEHeartbeatPack({
									timeDuration: 2000
								}, (ret) => {
									console.log('startSendBLEHeartbeatPack', ret)
								});

								// 5. 开始录音
								// 创建一个文件，用于保存录音数据
								isRecording = true
								pcmData = []
								sdkModule.sceneRecord(
									(ret) => {
										// console.log('record', ret)
										console.log('record', ret.success, ret.data.length)
										// this.toast('record ' + ret.success + ' ' + ret.data.length)
										// append ret.data to pcmData
										pcmData.push(...ret.data)
										this.pcmDataReceived += ret.data.length
								});
							});
						});
					});

				});
			},
			//初始化
			initBleSDK() {
				// testModule.init();
				console.log("initBleSDK os", plus.os.name);
				if (plus.os.name === 'iOS') {
					// iOS 平台
					sdkModule.init({
						enableDenoise: true
					});
				} else {
					// Android 平台
					// public Long init(boolean isNewDecoder, boolean enableDenoise, boolean debug)
					sdkModule.init({
						enableDenoise: true
					}, (ret) => {
						console.log('init', ret);
					});
				}

				// 如果是 iOS 平台，deviceProtocol 设置为 1
				// 如果是 Android 平台，deviceProtocol 设置为 16。Android 平台上 1 也能工作。
				var platform = uni.getSystemInfoSync().platform;
				if (platform === 'android') {
					deviceProtocol = 16;
				} else if (platform === 'ios') {
					deviceProtocol = 1;
				}

				//不需要设置的参数请注释掉
				sdkModule.initBleSDK({
					deviceProtocol: deviceProtocol // 1:BLE, 16:SPP，初始化后不能随便修改
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					this.toast(JSON.stringify(ret));
				});
			},
			isBlueEnable() {
				var ret = sdkModule.isBlueEnable();
				console.log(ret)
				this.toast(JSON.stringify(ret));
			},
			enableBluetooth() {
				sdkModule.enableBluetooth((ret) => {
					//扫描回调结果
					console.log(ret)
					this.toast(JSON.stringify(ret));
				});
			},
			disableBluetooth() {
				sdkModule.disableBluetooth((ret) => {
					//扫描回调结果
					console.log(ret)
					this.toast(JSON.stringify(ret));
				});
			},
			//开始扫描
			startScan() {
				this.scan_result = []
				sdkModule.startScan({
					//暂时未启动参数查询，由SDK内进行过滤筛选
				}, (ret) => {
					//扫描回调结果
					console.log("startScan", ret)
					// this.toast(JSON.stringify(ret));
					if (ret.success) {
						// append to scan_result
						this.scan_result.push(ret.data);
						if (ret.data.deviceId == this.getMacAddress()) {
							console.log('检测到指定设备', ret)
							this.toast(JSON.stringify(ret));
						} else {
							console.log('检测到其他设备')
						}
					}
				});
			},
			//停止扫描
			stopScan() {
				sdkModule.stopScan();
			},
			connect() {
				this.toast('开始连接 1');
				sdkModule.disconnect((ret) => {
					console.log('disconnect', ret);
					setTimeout(() => {
						this.toast('开始连接 2');
						var connectOptions = {
							macAddress: this.getMacAddress(),
							deviceMac: this.classicalAddress
						};
						console.log('connectOptions', connectOptions);
						sdkModule.connect(connectOptions, (ret) => {
							//扫描回调结果
							console.log("connect",ret)
							this.toast(JSON.stringify(ret));
						});
					}, 3000);
				})
			},
			disconnect() {
				sdkModule.disconnect((ret) => {
					//扫描回调结果
					console.log(ret)
					this.toast(JSON.stringify(ret));
				});
			},
			startHeartBeat() {
				sdkModule.unRegisterDataCallback();
				this.registerDataCallback();
				sdkModule.startSendBLEHeartbeatPack({
					timeDuration: 2000
				}, (ret) => {
					console.log('startSendBLEHeartbeatPack', ret)
				});
			},
			stopHeartBeat() {
				sdkModule.stopSendBLEHeartbeatPack((ret) => {
					console.log('stopSendBLEHeartbeatPack', ret)
				});
			},
			startOTA() {
				// 断开业务连接
				sdkModule.disconnect((ret) => {
					//扫描回调结果
					console.log("disconnect", ret)
					this.toast(JSON.stringify(ret));

					console.log("deviceProtocol", deviceProtocol);
					this.toast("deviceProtocol: " + deviceProtocol);
					var connectFun = sdkModule.connect;
					if (deviceProtocol === 16) {
						// SPP 模式
						connectFun = sdkModule.connectForOTAInSpp;
					}
					// 连接设备
					connectFun({
						/**
						 * {"success":true,"msg":"onLeScan","data":{"mBleAddress":"1AF92E22-C653-272E-06AF-46D92E4B8963","mDeviceType":2,"mBleName":"Fuwinda 6199"}}
						 */
						macAddress: this.getMacAddress(),
						deviceMac: this.classicalAddress
					}, (ret) => {
						//扫描回调结果
						console.log("connect", ret)
						this.toast(JSON.stringify(ret));

						// 连接失败，直接返回
						if (!ret.success) {
							return;
						}

						// 调用异步方法
						var filePath = plus.io.convertLocalFileSystemURL('/static/HTS283_BS685HL_2500YP_SW_V3.2_release_converted.bin') //pdf文件所在路径
						console.log(filePath)
						sdkModule.startOTA({
							localPath: filePath, //mac地址
							mClearUserData: false, //清楚用户数据
							mUpdateBtAddress: false, //是否更新蓝牙地址
							btAddress: '',//新的蓝牙地址，必须满足规则才生效
							mUpdateBtName: false, //是否更新蓝牙名称
							btName: '',//蓝牙名称，不为空才生效
							mUpdateBleAddress: false, //是否更新BLE地址
							bleAddress: '',//新的BLE蓝牙地址，必须满足规则才生效
							mUpdateBleName: false, //是否更新BLE蓝牙名称
							bleName: '', //BLE蓝牙名称，不为空才生效
							breakPoint: 0 //0不断点续传，1支持断点续传
						}, (ret) => {
							//扫描回调结果
							console.log("startOTA", ret)
							this.toast(JSON.stringify(ret));

							// OTA 成功后，重连
							// setTimeout(() => {
							// 	// OTA 结束后，断开连接。重新建立业务连接
							// 	sdkModule.disconnect((ret) => {
							// 		//扫描回调结果
							// 		console.log("disconnect", ret)
							// 		// modal.toast({
							// 		// 	//发送操作结果
							// 		// 	message: ret,
							// 		// 	duration: 1.5
							// 		// });

							// 		// 重新连接
							// 		sdkModule.connect({
							// 			/**
							// 			 * {"success":true,"msg":"onLeScan","data":{"mBleAddress":"1AF92E22-C653-272E-06AF-46D92E4B8963","mDeviceType":2,"mBleName":"Fuwinda 6199"}}
							// 			 */
							// 			macAddress: this.getMacAddress(),
							// 			deviceMac: this.classicalAddress
							// 		}, (ret) => {
							// 			//扫描回调结果
							// 			console.log("connect", ret)
							// 			// modal.toast({
							// 			// 	//发送操作结果
							// 			// 	message: ret,
							// 			// 	duration: 1.5
							// 			// });
							// 		});
							// 	});
							// }, 3000); // 等待耳机重启完成
						});
					});
				});
			},
			cancelOTA() {
				sdkModule.cancelOTA((ret) => {
					//扫描回调结果
					console.log(ret)
					this.toast(JSON.stringify(ret));
				});
			},
			startCallingRecord() {
				this.startRecord(1)
			},
			startMicrophoneRecord() {
				this.startRecord(2)
			},
			startRecord(mode) {
				var func = sdkModule.startRecord
				if (mode === 1) {
					func = sdkModule.startRecord
				} else if (mode === 2) {
					func = sdkModule.sceneRecord
				} else if (mode === 3) {
					func = sdkModule.audioVideoRecord
				}
				// 创建一个文件，用于保存录音数据
				isRecording = true
				pcmData = []
				sdkModule.startRecord(
					(ret) => {
						// console.log('record', ret)
						console.log('record', ret.success, ret.data.length)
						// this.toast('record ' + ret.success + ' ' + ret.data.length)
						// append ret.data to pcmData
						pcmData.push(...ret.data)
						this.pcmDataReceived += ret.data.length
					});
			},
			stopCallingRecord() {
				sdkModule.stopRecord((ret) => {
					console.log('stopCallingRecord', ret)
					this.toast(JSON.stringify(ret))

					// delay 5s to make sure the record is finished
					setTimeout(() => {
						isRecording = false

						// 将 pcmData 转为 Uint8Array
						var pcmDataArray = new Uint8Array(pcmData)
						// console.log('pcmDataArray', pcmDataArray)
						// 写入 plugin-demo-pcm.wave 文件
						console.log('write file', pcmDataArray.length);
						// check is plus ready
						if (!plus) {
							console.log('plus is not ready');
							return;
						}
						var that = this;
						plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
							dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
								dirEntry.getFile(filenameStub + '.pcm', {
									create: true
								}, (fileEntry) => {
									fileEntry.createWriter((writer) => {
										writer.onwrite = function(e) {
											console.log('write success', e);
											// export file
											// path on android: /storage/emulated/0/Android/data/com.android.UniPlugin/documents/pcm/plugin-demo-pcm.pcm
											// path of fileEntry
											console.log('fileEntry', fileEntry.fullPath);
											that.toast('write success ' + fileEntry.fullPath);
											that.saved_text_filepath = fileEntry.fullPath;
											// that.exportFile(fileEntry.fullPath)
										};
										writer.onerror = function(e) {
											console.log('write error', e);
										};
										console.log('write ' + pcmDataArray.length);
										// FIXME: 这里写二进制会失败，文件大小为0
										// 暂时写入字符串，然后用工具转为二进制
										// convert_comma_split_array_to_raw.py: 转化为二进制文件
										// split-channels.py: 分离左右声道
										var str = pcmDataArray.toString();
										// console.log('str', len(s));
										writer.write(str);
									}, (e) => {
										console.log('createWriter error', e);
										that.toast('createWriter error ' + JSON.stringify(e));
									});
								}, (e) => {
									console.log('getFile error', e);
									that.toast('getFile error ' + JSON.stringify(e));
								})
							}, (e) => {
								console.log('getDirectory error', e);
								that.toast('getDirectory error ' + JSON.stringify(e));
							})
						}, (e) => {
							console.log('requestFileSystem error', e);
							that.toast('requestFileSystem error ' + JSON.stringify(e));
						});
					}, 5000);
				})
			},
			sendTestData2() {
				sdkModule.write({
					hexStr: '5aa500'
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					this.toast(JSON.stringify(ret));
				});
			},
			registerDataCallback() {
				sdkModule.registerDataCallback((ret) => {
					console.log('callback', ret)
					// this.toast(JSON.stringify(ret));
					// if ret.data is "5bb500", it's a heartbeat response
					if (ret.data === '5bb500') {
						if (this.heartbeatStatusIcon === '✅') {
							this.heartbeatStatusIcon = '❌'
						} else {
							this.heartbeatStatusIcon = '✅'
						}
					}
				});
			},
			unRegisterDataCallback() {
				sdkModule.unRegisterDataCallback();
			},
			decoderOpus() {
				var ret = sdkModule.decoderOpus([0x00, 0x00, 0x00]);
				console.log(ret)
				//ret为[0x00, 0x00, 0x00]数组
			},
			waveToPcm() {
				sdkModule.convertWaveToPcm({
					wavePath: 'pcm/plugin-demo-pcm.wav',
					pcmPath: 'pcm/plugin-demo-pcm.pcm'
				}, (ret) => {
					console.log(ret)
				});
			},
			pcmToWav() {
				var that = this;
				// raw pcm file path
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
						dirEntry.getFile(filenameStub + '-raw.pcm', {
							create: true
						}, (fileEntry) => {
							var pcmFilepath = fileEntry.fullPath;
							console.log('pcmFilepath', pcmFilepath);
							var wavFilepath = pcmFilepath.replace('.pcm', '-wav.wav');
							sdkModule.convertPcmToWave({
								pcmPath: pcmFilepath,
								wavPath: wavFilepath
							}, (ret) => {
								console.log(ret)
								that.toast(JSON.stringify(ret));
							});
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			textToRawPcm() {
				var textFilename = filenameStub + '.pcm';
				this.doTextToRawPcm(textFilename);
			},
			doTextToRawPcm(textFilename, successCallback) {
				var that = this;
				// string array file path
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
						dirEntry.getFile(textFilename, {
							create: true
						}, (fileEntry) => {
							var textFilepath = fileEntry.fullPath;
							console.log('textFilepath', textFilepath);
							var pcmFilepath = textFilepath.replace('.pcm', '-raw.pcm');
							sdkModule.convertStringArrayFileToRawFile({
								textPath: textFilepath,
								pcmPath: pcmFilepath
							}, (ret) => {
								console.log(ret)
								that.toast(JSON.stringify(ret));
								if (successCallback) {
									successCallback();
								}
							});
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			splitChannels() {
				this.doSplitChannels(filenameStub);
			},
			doSplitChannels(myFilenameStub, successCallback) {
				console.log('splitChannels', myFilenameStub + '.pcm');
				// split string array pcm file to left and right channel
				var that = this;
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
						dirEntry.getFile(myFilenameStub + '.pcm', {
							create: true
						}, (fileEntry) => {
							// read file
							fileEntry.file((file) => {
								var reader = new plus.io.FileReader();
								reader.onloadend = function(e) {
									var pcmData = e.target.result;
									console.log('pcmData', pcmData.length);
									// split pcmData by comma
									var pcmArray = pcmData.split(',');
									console.log('pcmArray', pcmArray.length);
									// split pcmArray to left and right channel
									var leftChannel = [];
									var rightChannel = [];
									// left channel: 0, 1, 4, 5, 8, 9...
									// right channel: 2, 3, 6, 7, 10, 11...
									for (var i = 0; i < pcmArray.length; i+=4) {
										leftChannel.push(pcmArray[i]);
										leftChannel.push(pcmArray[i + 1]);
										rightChannel.push(pcmArray[i + 2]);
										rightChannel.push(pcmArray[i + 3]);
									}

									// write leftChannel to left.pcm
									var leftChannelStr = leftChannel.join(',');
									console.log('leftChannelStr', leftChannelStr.length);
									var that2 = that;
									that.writeChannelDataToFile(that, leftChannelStr, myFilenameStub, 'left', () => {
										console.log('write left success');
										that2.toast('write left success');

										// convert left string array file to raw file
										that2.doTextToRawPcm(myFilenameStub + '-left.pcm', () => {
											console.log('convert left success', myFilenameStub + '-left.pcm');
											that2.toast('convert left success ' + myFilenameStub + '-left.pcm');

											// write rightChannel to right.pcm
											var rightChannelStr = rightChannel.join(',');
											console.log('rightChannelStr', rightChannelStr.length);
											var that3 = that2;
											that2.writeChannelDataToFile(that2, rightChannelStr, myFilenameStub, 'right', () => {
												console.log('write right success');
												that3.toast('write right success');

												// convert right string array file to raw file
												that3.doTextToRawPcm(myFilenameStub + '-right.pcm', () => {
													console.log('convert right success', myFilenameStub + '-right.pcm');
													that3.toast('convert right success ' + myFilenameStub + '-right.pcm');

													if (successCallback) {
														successCallback();
													}
												});
											});
										});
									});
								};
								reader.readAsText(file);
							}, (e) => {
								console.log('file error', e);
							});
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			splitChannelsTest() {
				//
				// 生成一个长度为 200 的测试文件，用于测试分离左右声道
				// 文件内容为：0,1,2,3,4...199
				// 然后拆分左右声道，检查左声道文件和右声道文件是否正确
				// 左声道的内容应该为：0,1,4,5,8,9...
				// 右声道的内容应该为：2,3,6,7,10,11...
				//
				var myFilenameStub = 'plugin-demo-split-channels-test';
				// generate test file
				var testFileContent = '';
				for (var i = 0; i < 200; i++) {
					testFileContent += i + ',';
				}
				// 去掉最后一个逗号
				testFileContent = testFileContent.substring(0, testFileContent.length - 1);
				console.log('testFileContent', testFileContent.length);
				var that = this;
				// 写入文件 myFilenameStub + '.pcm'
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) =>{
						dirEntry.getFile(myFilenameStub + '.pcm', {
							create: true
						}, (fileEntry) => {
							fileEntry.createWriter((writer) => {
								writer.onwrite = function(e) {
									console.log('write success', e);
									var that2 = that;
									// split channels
									that.doSplitChannels(myFilenameStub, () => {
										console.log('split channels success');

										//
										// 检查左声道文件和右声道文件是否正确
										//

										// check left channel
										plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
											dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
												dirEntry.getFile(myFilenameStub + '-left.pcm', {
													create: true
												}, (fileEntry) => {
													// read file
													fileEntry.file((file) => {
														var reader = new plus.io.FileReader();
														reader.onloadend = function(e) {
															var pcmData = e.target.result;
															console.log('pcmData', pcmData.length);
															// split pcmData by comma
															var pcmArray = pcmData.split(',');
															console.log('pcmArray', pcmArray.length);

															// check left channel
															// 左声道的内容应该为：0,1,4,5,8,9...
															var valPrevious = '0'
															for (var i = 0; i < pcmArray.length; i++) {
																var valExpected = ''
																if (i % 2 === 0) {
																	valExpected = '' + (i * 2);
																} else {
																	// valPrevious to int, and add 1
																	valExpected = '' + (parseInt(valPrevious) + 1);
																}
																if (pcmArray[i] !== valExpected) {
																	console.log('left channel error', i, pcmArray[i], valExpected);
																	break;
																}
																valPrevious = pcmArray[i];
															}
															if (i === pcmArray.length) {
																console.log('left channel success');
																that2.toast('left channel success');
															}
														};
														reader.readAsText(file);
													}, (e) => {
														console.log('file error', e);
													});
												}, (e) => {
													console.log('getFile error', e);
												})
											}, (e) => {
												console.log('getDirectory error', e);
											})
										}, (e) => {
											console.log('requestFileSystem error', e);
										});

										// check right channel
										plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
											dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
												dirEntry.getFile(myFilenameStub + '-right.pcm', {
													create: true
												}, (fileEntry) => {
													// read file
													fileEntry.file((file) => {
														var reader = new plus.io.FileReader();
														reader.onloadend = function(e) {
															var pcmData = e.target.result;
															console.log('pcmData', pcmData.length);
															// split pcmData by comma
															var pcmArray = pcmData.split(',');
															console.log('pcmArray', pcmArray.length);

															// check right channel
															// 右声道的内容应该为：2,3,6,7,10,11...
															var valPrevious = '2'
															for (var i = 0; i < pcmArray.length; i++) {
																var valExpected = ''
																if (i % 2 === 0) {
																	valExpected = '' + (i * 2 + 2);
																} else {
																	// valPrevious to int, and add 1
																	valExpected = '' + (parseInt(valPrevious) + 1);
																}
																if (pcmArray[i] !== valExpected) {
																	console.log('right channel error', i, pcmArray[i], valExpected);
																	break;
																}
																valPrevious = pcmArray[i];
															}
															if (i === pcmArray.length) {
																console.log('right channel success');
																that2.toast('right channel success');
															}
														};
														reader.readAsText(file);
													}, (e) => {
														console.log('file error', e);
													});
												}, (e) => {
													console.log('getFile error', e);
												})
											}, (e) => {
												console.log('getDirectory error', e);
											})
										}, (e) => {
											console.log('requestFileSystem error', e);
										});
									});
								};
								writer.onerror = function(e) {
									console.log('write error', e);
								};
								console.log('write ' + testFileContent.length);
								writer.write(testFileContent);
							}, (e) => {
								console.log('createWriter error', e);
							})
						}, (e) => {
							console.log('getFile error', e);
						})
					})
				})
			},
			denoisePcmFile() {
				var that = this;
				this.doDenoisePcmFile(filenameStub + '-left-raw.pcm', () => {
					console.log('denoise left success');
					that.toast('denoise left success');

					var that2 = that;
					that.doDenoisePcmFile(filenameStub + '-right-raw.pcm', () => {
						that2.toast('denoise success');
					});
				});
			},
			doDenoisePcmFile(filename, successCallback) {
				this.toast('denoise ' + filename);
				var that = this;
				// denoise left channel pcm file
				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', {create:true}, (dirEntry) => {
						dirEntry.getFile(filename, {
							create: true
						}, (fileEntry) => {
							var pcmFilepath = fileEntry.fullPath;
							console.log('pcmFilepath', pcmFilepath);
							var denoiseFilepath = pcmFilepath.replace('.pcm', '-denoise.pcm');
							sdkModule.denoisePcmFile({
								pcmPath: pcmFilepath,
								denoisePath: denoiseFilepath
							}, (ret) => {
								console.log(ret)
								that.toast(JSON.stringify(ret));
								if (successCallback) {
									successCallback();
								}
							});
						}, (e) => {
							console.log('getFile error', e);
						})
					}, (e) => {
						console.log('getDirectory error', e);
					})
				}, (e) => {
					console.log('requestFileSystem error', e);
				});
			},
			writeChannelDataToFile(that, channelDataStr, myFilenameStub, side, successCallback) {
				console.log('writeChannelDataToFile', side, channelDataStr.length);

				plus.io.requestFileSystem(plus.io.PUBLIC_DOCUMENTS, (dir) => {
					dir.root.getDirectory('pcm', { create: true }, (dirEntry) => {
					dirEntry.getFile(myFilenameStub + '-'+ side + '.pcm', {
						create: true
					}, (fileEntry) => {
						fileEntry.createWriter((writer) => {
							writer.onwrite=function(e) {
								console.log('write success', e)
								// export file
								// path on android: /storage/emulated/0/Android/data/com.android.UniPlugin/documents/pcm/plugin-demo-pcm.pcm
								// path of fileEntry
								console.log('fileEntry', fileEntry.fullPath)
								that.toast('write success '+fileEntry.fullPath)
								// that.exportFile(fileEntry.fullPath)
								if (successCallback) {
									successCallback()
								}
							}
							writer.onerror=function(e) {
								console.log('write error', e)
							}
							console.log('write '+channelDataStr.length)
							writer.write(channelDataStr)
						}, (e) => {
							console.log('createWriter error', e)
							that.toast('createWriter error '+JSON.stringify(e))
						})
					}, (e) => {
						console.log('getFile error', e)
						that.toast('getFile error '+JSON.stringify(e))
					})
					}, (e) => {
						console.log('getDirectory error', e)
						that.toast('getDirectory error '+JSON.stringify(e))
					})
				}, (e) => {
					console.log('requestFileSystem error', e)
					that.toast('requestFileSystem error '+JSON.stringify(e))
				})
			}
		},
	}
</script>

<!-- #ifdef APP -->
<script module="yourModuleName" lang="renderjs"> //此模块内部只能用选项式API风格，vue2、vue3均可用，请照抄这段代码；不可改成setup组合式API风格，否则可能不能import vue导致编译失败
/**需要编译成App时，你需要添加一个renderjs模块，然后一模一样的import上面那些js（微信的js除外）
    ，因为App中默认是在renderjs（WebView）中进行录音和音频编码**/
import 'recorder-core'
import RecordApp from 'recorder-core/src/app-support/app'
import '../../uni_modules/Recorder-UniCore/app-uni-support.js' //renderjs中似乎不支持"@/"打头的路径，如果编译路径错误请改正路径即可

//按需引入你需要的录音格式支持文件，和插件
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine' 

import 'recorder-core/src/extensions/waveview'

export default {
    mounted(){
        //App的renderjs必须调用的函数，传入当前模块this
        RecordApp.UniRenderjsRegister(this);
    },
    methods: {
        //这里定义的方法，在逻辑层中可通过 RecordApp.UniWebViewVueCall(this,'this.xxxFunc()') 直接调用
        //调用逻辑层的方法，请直接用 this.$ownerInstance.callMethod("xxxFunc",{args}) 调用，二进制数据需转成base64来传递
    }
}
</script>
<!-- #endif -->