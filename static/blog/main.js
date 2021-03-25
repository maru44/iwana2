// cookie
const getCookie = name => {
    if (document.cookie && document.cookie !== '') {
        for (const cookie of document.cookie.split(';')){
            const [key, value] = cookie.trim().split('=');
            if(key === name) {
                return decodeURIComponent(value);
            }
        }
    }
};

// get csrftoken
let csrftoken = getCookie('csrftoken');

// is_gotten change
let gottenChange = (btn) => {
    // get slug of Wanted
    const slug = $(btn).attr("wanted");
    //console.log(slug);

    // fetch and change is_gotten
    fetch(`/api/wanted/${slug}`, {
        method: "GET",
    })
    .then((res) => {
        return res.json();
    })
    .then((res) => {
        if (res.is_) {
            $(btn).children(".is_gotten").html('&#10004;');
            $(".have").removeClass("off");
            $(".notHave").addClass("off");
        } else {
            $(btn).children(".is_gotten").html('');
            $(".have").addClass("off");
            $(".notHave").removeClass("off");
        }
    })
    .catch((err) => {
        console.log(err);
    })
}

// offer posting
let postOffer = () => {
    const offer_url = $('input:text[name="offer"]').val();
    // only if offer_url is not null
    if (offer_url) {
        data = {
            "offer_url": offer_url,
        }
        // fetch to endpoint
        fetch(`/api${location.pathname}`, {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "Content-Type": "application/json; charset=utf-8",
                "X-CSRFToken": csrftoken,
            },
        })
        .then((res) => {
            return res.json();
        })
        .then((res) => {
            // input => blank
            $('input:text[name="offer"]').val('');
            offerAdd(res);
        })
        .catch((err) => {
            console.log(err);
        })
    };
};

// add offer elements
let offerAdd = (response) => {
    let addEl;
    if (response.user) {
        addEl = `<div class="flexNormal mb10 alCen"><div class="mr10  hrefBox"><div class="offerUserArea">` +
        `<div class="imgCircle mla mra" style="background-image: url('${response.user.picture}'); width: 30px; height: 30px;"></div>` +
        `</div><a href="/wanteds/${response.user.username}" class="hrefBoxIn"></a>` +
        `</div><article class="flex1 aOffer"><div class="ml10"><p class="brAll">${response.offer_url}</p>` +
        `<div class="mt5 textRight"><small>今</small></div></article></div>`
    } else {
        addEl = `<div class="flexNormal mb10 alCen"><article class="flex1 aOffer"><div class="ml10"><p class="brAll">${response.offer_url}</p>` +
        `<div class="mt5 textRight"><small>今</small></div></article></div>`
    }
    $(addEl).prependTo(".offerList")
};


let globalData = (word) => {
    data = {
        "keyword": word,
        "sold": $("#sold_select").val(),
        "category": $("#category_select").val(),
    }
    fetch('/api/scrape/', {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json; charset=utf-8",
            "X-CSRFToken": csrftoken,
        }
    })
    .then((res) => {
        return res.json();
    })
    .then((res) => {
        let mer = res["mercari"];
        let rak = res["rakuma"];
        let yah = res["yahoo"];
        for (let i = 0; i < mer.length; i++) {
            genLinkEl("mercari", mer[i]);
        }
        for (let i = 0; i < rak.length; i++) {
            genLinkEl("rakuma", rak[i]);
        }
        for (let i = 0; i < yah.length; i++) {
            genLinkEl("yahoo", yah[i])
        }
    })
    .then(() => {
        $(".aMess p").html(`検索が完了しました。`)
    })
    .catch((err) => {
        console.log(err);
    })
}

// generate link elements
// for global search
let genLinkEl = (which, dict) => {
    let color = "";
    let so = "";
    if (dict["sold"]) {
        color = "background-color: rgba(255, 255, 255, .6)";
        so = "SOLD OUT";
    }
    let newEl = `<div class="alCen hrefBox mt5 scrapeTable mb20">` +
        `<div class="frameContain" style="background-image: url('${dict["image"]}');"></div>` +
        `<div class="w100 f14px noWrap ovHide mt5">${dict["name"]}</div>` +
        `<div class="mla scrapePrice f14px">${dict["price"]}</div>` +
        `<a target="_new" href="${dict["href"]}" class="hrefBoxIn flexCen" style="${color}"><p>${so}</p></a></div>`
    console.log(dict["image"]);
    $(`.${which}Area`).append(newEl);
}

// select all platform
let checkPlatAll = btn => {
    console.log(btn);
    if ($(btn).prop('checked')) {
        $('input[name="wanted_plat"]').prop('checked', true);
    } else {
        $('input[name="wanted_plat"]').prop('checked', false);
    }
}


$(() => {
    // offer btn push
    $("#offeringBtn").click(() => {
        postOffer();
    })

    // change is_gotten
   $(".gottenBtn").on('click', (e) => {
       // console.log($(e.target));
       // console.log($(e.currentTarget));
       gottenChange($(e.currentTarget));
   })

    // modal close general
    $(".modal, .closeModal").click(() => {
        $(".modal").addClass("off");
        $(".modalCon").addClass("off");
    })

    // logout modal open
    $(".logoutStart").click(() => {
        $(".modal").removeClass("off");
        $(".modalConLogout").removeClass("off");
    })

    // riyoukiyaku modal
    $("#kiyakuOpen").click(() => {
        $(".modal").removeClass("off");
        $(".modalConKiyaku").removeClass("off");
    })

    // delete wanted modal open
    $(".delWantedBtn").click(() => {
        $(".modal").removeClass("off");
        $(".modalDelWanted").removeClass("off");
    })

    // riyoukiyaku input checked
    $("#kiyakuInput").click(() => {
        if ($("#regiSub").prop("disabled")) {
            $("#regiSub").prop("disabled", false);
        } else {
            $("#regiSub").prop("disabled", true);
        }
    })

    // global search
    $("#globalBtn").click(() => {
        let word = $("#globalStr").val();
        if (word) {
            $(".mercariArea").empty();
            $(".rakumaArea").empty();
            $(".yahooArea").empty();
            $(".messZone").removeClass("off");
            $(".aMess p").html(`${word}を検索中`);
            globalData(word);
        }
    })

    $('input[name="plat_all"]').change( e => {
        checkPlatAll(e.currentTarget);
    })
});