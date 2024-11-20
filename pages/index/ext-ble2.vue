<template>

	<div>
		<text>BLE蓝牙相关接口</text>
		<button type="primary" @click="initBleSDK">初始化</button>
		<button type="primary" @click="isBlueEnable">蓝牙是否开启</button>
		<button type="primary" @click="enableBluetooth">打开蓝牙</button>
		<button type="primary" @click="disableBluetooth">关闭蓝牙</button>
		<button type="primary" @click="startScan">开始扫描</button>
		<button type="primary" @click="stopScan">停止扫描</button>
		<button type="primary" @click="connect">连接</button>
		<button type="primary" @click="disconnect">断开连接</button>
		<button type="primary" @click="startOTA">开始OTA</button>
		<button type="primary" @click="cancelOTA">取消OTA</button>
		<button type="primary" @click="sendTestData">发送数据</button>
		<button type="primary" @click="sendTestData2">发送心跳</button>
		<button type="primary" @click="registerDataCallback">注册监听器</button>
		<button type="primary" @click="unRegisterDataCallback">取消注册监听器</button>
		<button type="primary" @click="decoderOpus">解码opus</button>
	</div>
</template>

<script>
	// 获取 module 
	var sdkModule = uni.requireNativePlugin("XM-BesAllModule")
	// var testModule = uni.requireNativePlugin("TestModule")
	const deviceProtocol = 16
	// const modal = uni.requireNativePlugin('modal');
	export default {
		data() {
			return {
				// address: "94F206C6-42EE-8395-3CE1-3A8F15FA57FD"
				// address: "EE:11:22:33:C1:79"//By Macro
				address: "EE:11:22:33:3D:78", // tz test device ble address
				classicalAddress: "11:11:22:33:3D:78" // tz test device classical address
				// address: "EE:11:22:33:BF:84", // tz xl test device ble address
				// classicalAddress: "11:11:22:33:BF:84" // tz xl test device classical address
			}
		},
		onLoad() {

		},
		methods: {
			//初始化
			initBleSDK() {
				// testModule.init();

				//不需要设置的参数请注释掉
				sdkModule.initBleSDK({
					deviceProtocol: deviceProtocol // 1:BLE, 16:SPP，初始化后不能随便修改
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			isBlueEnable() {
				var ret = sdkModule.isBlueEnable();
				console.log(ret)
			},
			enableBluetooth() {
				sdkModule.enableBluetooth((ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			disableBluetooth() {
				sdkModule.disableBluetooth((ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			//开始扫描
			startScan() {
				sdkModule.startScan({
					//暂时未启动参数查询，由SDK内进行过滤筛选
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					if (ret.success) {
						if (ret.data.deviceId == this.address) {
							console.log('检测到指定设备', ret)
						} else {
							console.log('检测到其他设备')
						}
					// 	modal.toast({
					// 		//发送操作结果
					// 		message: ret,
					// 		duration: 1.5
					// 	});
					}
				});
			},
			//停止扫描
			stopScan() {
				sdkModule.stopScan();
			},
			connect() {
				sdkModule.connect({
					/**
					 * {"success":true,"msg":"onLeScan","data":{"mBleAddress":"1AF92E22-C653-272E-06AF-46D92E4B8963","mDeviceType":2,"mBleName":"Fuwinda 6199"}}
					 */
					macAddress: this.address,
					deviceMac: this.classicalAddress
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			disconnect() {
				sdkModule.disconnect((ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			startOTA() {
				// 断开业务连接
				sdkModule.disconnect((ret) => {
					//扫描回调结果
					console.log("disconnect", ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });

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
						macAddress: this.address,
						deviceMac: this.classicalAddress
					}, (ret) => {
						//扫描回调结果
						console.log("connect", ret)
						// modal.toast({
						// 	//发送操作结果
						// 	message: ret,
						// 	duration: 1.5
						// });

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
							// modal.toast({
							// 	//发送操作结果
							// 	message: ret,
							// 	duration: 1.5
							// });

							setTimeout(() => {
								// OTA 结束后，断开连接。重新建立业务连接
								sdkModule.disconnect((ret) => {
									//扫描回调结果
									console.log("disconnect", ret)
									// modal.toast({
									// 	//发送操作结果
									// 	message: ret,
									// 	duration: 1.5
									// });

									// 重新连接
									sdkModule.connect({
										/**
										 * {"success":true,"msg":"onLeScan","data":{"mBleAddress":"1AF92E22-C653-272E-06AF-46D92E4B8963","mDeviceType":2,"mBleName":"Fuwinda 6199"}}
										 */
										macAddress: this.address,
										deviceMac: this.classicalAddress
									}, (ret) => {
										//扫描回调结果
										console.log("connect", ret)
										// modal.toast({
										// 	//发送操作结果
										// 	message: ret,
										// 	duration: 1.5
										// });
									});
								});
							}, 3000); // 等待耳机重启完成
						});
					});
				});
			},
			cancelOTA() {
				sdkModule.cancelOTA((ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			sendTestData() {
				sdkModule.write({
					hexStr: '5aa501'
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			sendTestData2() {
				sdkModule.write({
					hexStr: '5aa500'
				}, (ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			registerDataCallback() {
				sdkModule.registerDataCallback((ret) => {
					//扫描回调结果
					console.log(ret)
					// modal.toast({
					// 	//发送操作结果
					// 	message: ret,
					// 	duration: 1.5
					// });
				});
			},
			unRegisterDataCallback() {
				sdkModule.unRegisterDataCallback();
			},
			decoderOpus() {
				var ret = sdkModule.decoderOpus([0x00, 0x00, 0x00]);
				console.log(ret)
				//ret为[0x00, 0x00, 0x00]数组
			}
		}
	}
</script>