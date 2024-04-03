function load_tags(event){

    let inputel = event.target;
    let inputelId = inputel.getAttribute('id');
    let inputel_list = inputel.value.split(',');
    let input_tag = inputel_list.slice(-1);

    // vas chercher le resultat de l'url en fonction de la valeur dans input (views autocomplition)
    let promesse = fetch("/auto/?nom=" + input_tag);
    promesse.then((response) => {
        return response.text();
    }).then((text) => {

        let tags_list = JSON.parse(text);

        let form = inputel.parentElement;
        form.getElementsByClassName("jscomp");

        if (form.getElementsByClassName("jscomp").length!=0) {
            let panels = form.getElementsByClassName("jscomp");
            for (let el of panels){
                el.remove();
            }
        }

        let panel = document.createElement("div");
        panel.setAttribute("class", "jscomp");
        panel.setAttribute("id", inputelId+"div")
        
        
        form.appendChild(panel);
        let ul = document.createElement("ul");
        ul.setAttribute("class", inputelId+"ul");
                
        for ( let tag_name of tags_list) {
            
            if (!inputel_list.includes((" ")+tag_name)){
                
                let li = document.createElement("li");
                li.setAttribute("class", inputelId+"li");
                let tags = document.createElement("p");
                tags.setAttribute("class", inputelId+"p");
                tags.textContent = tag_name;
                li.appendChild(tags);
                ul.appendChild(li);

                function selectionTags(){
                    let inputel_list = inputel.value.split(',');
                    let liste_choix = inputel_list.slice(0, -1);
                    liste_choix.push((" ")+tag_name+(","));
                    inputel.value = liste_choix;
                            
                    if (form.getElementsByClassName("jscomp").length!=0) {
                        let panels = form.getElementsByClassName("jscomp");
                        for (let el of panels){
                            el.remove();
                        }
                    } 
                }

                li.addEventListener("click", selectionTags);
            }
        }
        panel.appendChild(ul);     
    })
}

function registerAutoCompletion(inputelSelector){
    let inputel = document.querySelector(inputelSelector);
    if (inputel != null){
        let inputelId = inputel.getAttribute('id');
        let selection=0;
        let form = inputel.parentElement;
        inputel.addEventListener("input", load_tags);
        form.getElementsByClassName("jscomp");
        inputel.addEventListener("keydown", function(event) {
            
            if (event.key == "ArrowDown"){
                event.preventDefault();
                if (form.getElementsByClassName("select").lenght!=0) {
                    let lisupclass = form.getElementsByClassName("select")
                    for (let ele of lisupclass){
                        ele.removeAttribute('class','select');
                        ele.removeAttribute("id", inputelId+"select");
                    }
                }
    
                let maxselect = form.getElementsByTagName('li').length;
                let listselect = form.getElementsByTagName('li')[selection];
                listselect.setAttribute("class", "select");
                listselect.setAttribute("id", inputelId+"select");
    
                if (selection < maxselect -1){
                    selection = selection +1;
                }else{
                    selection = maxselect-1;
                }
            } 
            if (event.key == "ArrowUp") {
                event.preventDefault();
                if (selection <= 0 ){
                    selection = 0;
                }else{
                    selection = selection -1;
                }
                let lisupclass = form.getElementsByClassName("select");
                if (lisupclass.lenght!=0) {
                    for (let ele of lisupclass){
                        ele.removeAttribute('class', 'select');
                        ele.removeAttribute("id", inputelId+"select");
                    }
                }
                let listselect = form.getElementsByTagName('li')[selection];
                listselect.setAttribute("class", "select");
                listselect.setAttribute("id", inputelId+"select");
            }
    
            if (event.key == "Enter") {
                event.preventDefault();
                li = form.getElementsByClassName('select');
                if(li.lenght!=0){
                    let tag_name = form.getElementsByClassName('select')[0].innerText;
                    let inputel_list = inputel.value.split(',');
                    liste_choix = inputel_list.slice(0, -1);
                    tagsAjout = liste_choix.push((" ")+tag_name+(","));
                    inputel.value = liste_choix;
                }
    
                if (form.getElementsByClassName("jscomp").length!=0) {
                    let panels = form.getElementsByClassName("jscomp");
                    for (let el of panels){
                        el.remove();
                    }
                }
            }
    
        })
        document.addEventListener("click", function() {
            if (form.getElementsByClassName("jscomp").length!=0) {
                let panels = form.getElementsByClassName("jscomp");
                for (let el of panels){
                    el.remove();
                }
            }
        })

    }

}
registerAutoCompletion("#addSnippetTags");

