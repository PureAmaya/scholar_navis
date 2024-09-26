
//夜晚模式
var isNightMode = false;
var btn_ladda;

function getCookie(name) {
    var cookieArray = document.cookie.split(';');
    for (var i = 0; i < cookieArray.length; i++) {
        var cookiePair = cookieArray[i].split('=');
        if (name == cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}

function toggleNightMode(is_switch) {
    if (is_switch) { isNightMode = !isNightMode; }

    if (!isNightMode) {
        $('body').addClass('night-mode');
    } else {
        $('body').removeClass('night-mode');
    }
}



// pdf获取全文
async function pdf_loader(data) {
    const typedarray = new Uint8Array(data);
    var fullText = '';

    // 使用 PDF.js 加载 PDF 文档
    var loadingTask = await pdfjsLib.getDocument(typedarray);
    var pdfDoc = await loadingTask.promise

    // 递归函数来处理每一页
    async function processPage(pageNum) {
        page = await pdfDoc.getPage(pageNum);
        textContent = await page.getTextContent();
        
        // 遍历文本内容并添加到全文中
        textContent.items.forEach(function (item) {
            fullText += item.str + ' ';
        });

        if (pageNum == 1) { fullText += '\n############FIRST PAGE################\n'; } //第一页标记一下

        pageNum++;
        // 检查是否还有更多的页面需要处理
        if (pageNum <= pdfDoc.numPages) {
            await processPage(pageNum);
        }
    }
    await processPage(1);
    return fullText;
}

// 并发读取pdf内容
async function process_file(file_entry) {
    blob_ = await file_entry.async('blob');
    array_buffer = await readFile(blob_);
    return await pdf_loader(array_buffer);

}

async function process_file_list(fileNameList, fileEntryList) {
    const promises = fileEntryList.map(file_entry => process_file(file_entry));
    const results = await Promise.all(promises);
    return [fileNameList, results];
}

async function push_to_download(fileNameList, fileEntryList) {
    var zip = new JSZip();
    $.each(fileEntryList, function (index, value) {
        zip.file(fileNameList[index] + ".simpl-pdf", value);
    })
    var zip_file = await zip.generateAsync({ type: "blob" });
    return zip_file;
}

function readFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        // 选择合适的读取方法
        reader.readAsArrayBuffer(file); // 或者 readAsText, readAsDataURL 等
    });
}


function submit_file(file_evt) {
    const $result = $("#result");
    var upload_filename = '';
    // remove content
    $result.html("");
    // Closure to capture the file information.
    function handleFile(f) {
        upload_filename = f.name;

        $('.loader-overlay').show(); //遮罩加载
        
        var $title = $("<h4>", {
            text: f.name
        });
        $result.append($title);

        var dateBefore = new Date();
        JSZip.loadAsync(f)                                   // 1) read the Blob
            .then(zip => {
                var dateAfter = new Date();
                $title.append($("<span>", {
                    "class": "small",
                    text: " (loaded in " + (dateAfter - dateBefore) + "ms)"
                }));

                var fileEntryList = [];
                var fileNameList = []; 
                zip.forEach(function (relativePath, zipEntry) {  // 2) print entries
                    if (zipEntry.name.slice(-4).toLowerCase() == '.pdf') {

                        // 储存压缩包内的文件，便于pdf.js使用
                        fileEntryList.push(zipEntry);
                        fileNameList.push(zipEntry.name)
                    }
                })

                return [fileNameList, fileEntryList]
            })
            // 交给pdf.js处理，获取全文
            .then(function (pdf_info) {
                var fileNameList = pdf_info[0]; var fileEntryList = pdf_info[1];
                return process_file_list(fileNameList, fileEntryList)
            })
            // 输出下载
            .then(function (pdf_content_info) {
                var fileNameList = pdf_content_info[0]; var fileContentList = pdf_content_info[1];
                push_to_download(fileNameList, fileContentList)
                    .then(dl_file => {
                        var $dl_button = $('<button id="dl_btn">点击下载</button>');
                        $('body').append($dl_button);

                        $dl_button.click(function () {
                            fileSaver.saveAs(dl_file, 'Simpl - ' + upload_filename);
                        });
                        // 计算总用时
                        var dateAfter = new Date();
                        $title.append($("<span>", {
                            "class": "small",
                            text: " (processed in " + (dateAfter - dateBefore) + "ms)"
                        }));
                        $('.loader-overlay').hide();
                        $('#sb_btn').remove();
                    });
            })

    }

    // 原本是想选择多个的，但是太麻烦了，先只允许一个zip压缩包吧
    var files = file_evt.target.files;
    for (var i = 0; i < files.length; i++) {

        if (files[i].type != 'application/zip' && files[i].type != 'application/x-zip-compressed') {
            alert('不支持的文件类型。请选择一个 ZIP 压缩包');
            return;
        }
        handleFile(files[i]);
    }
    $('#sb_btn').remove();
}

function on_file_selected() {
    $("#file_selector").on('change', function (evt) {

        var dl_btn = $('#dl_btn');
            if (dl_btn.length > 0) {dl_btn.remove();}
        
        var $sb_btn = $('#sb_btn');
        if ($sb_btn.length === 0){
            var button = $('<button id="sb_btn">确认</button>'); // 创建提交按钮
            $('body').append(button);
            button.click(() => {
                submit_file(evt);
                button.hide(); // 隐藏掉这个按钮，保证继续执行
            })
        }

    })
}

window.onload = function () {
    isNightMode = getCookie('js_darkmode_cookie') === 'False';
    toggleNightMode(false)
    $('#toggleNightMode').click(() => { toggleNightMode(true) });
    on_file_selected();
};


