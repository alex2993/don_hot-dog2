let user = {}
let currentUser;
let allUsers;


document.addEventListener('DOMContentLoaded', (ev) => {
    if (localStorage.getItem("curr-user")) {
        currentUser = JSON.parse(localStorage.getItem("curr-user"))
        document.getElementById('username').textContent = currentUser.name
        document.getElementById('phoneNumber').textContent = `Номер телефона: ${currentUser.contactInfo.phone}`
        document.getElementById('profil').style.display = "flex"
        document.getElementsByClassName('bonuses')[0].style.display = "grid"
        document.getElementsByClassName('zakazi')[0].style.display = "grid"
        document.getElementById('exitAcc').style.display = "block"
        if (currentUser.admin == true) {
            document.getElementById('adminPanel').style.display = "flex"
        }
    }
    
})


document.getElementById('buttonReg').addEventListener('click', (ev) => {
    ev.preventDefault()
    let form = document.forms.regForm
    let name = form.name.value
    let number = form.phone.value
    let adr = form.adres.value

    user.name = `${name}`
    user.phone = `${number}`
    user.adres = `${adr}`
    addUser(user)
})

document.getElementById('exitAcc').addEventListener('click', (ev) => {
    localStorage.removeItem("curr-user")
    document.getElementById('username').textContent = "Acc name"
        document.getElementById('phoneNumber').textContent = `Номер телефона: ####`
        document.getElementById('profil').style.display = "none"
        document.getElementsByClassName('bonuses')[0].style.display = "none"
        document.getElementsByClassName('zakazi')[0].style.display = "none"

        currentUser = ""

        document.getElementById('exitAcc').style.display = "none"
        document.getElementById('adminPanel').style.display = "none"
})



async function  addUser() {
    let response = await fetch('http://localhost:8080/add', {    
        method: 'POST',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: JSON.stringify(user)
      })
      if (response.status == 200) {
        alert("Registered")
      } else {
        alert("Start database")
      }
      
}

async function deleteAllUsers(id) {
    let response = await fetch(`http://localhost:8080/user/deleteAll/${id}`, {    
        method: 'DELETE',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      if (response.status == 200) {
        alert("Deleted")
      } else {
        alert("Start database")
      }
      
}

async function deleteAllOtzivs() {
    let response = await fetch('http://localhost:8080/posts/deleteAll', {    
        method: 'DELETE',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      if (response.status == 200) {
        alert("Deleted")
      } else {
        alert("Start database")
      }
      
}

async function deleteOtzivById(id) {
    let response = await fetch(`http://localhost:8080/posts/delete/${id}`, {    
        method: 'DELETE',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      if (response.status == 200) {
        alert(`Deleted post: ${id}`)
      } else {
        alert("Start database")
      }
      
}

async function deleteAllWorkSends() {
    let response = await fetch('http://localhost:8080/work/deleteAll', {    
        method: 'DELETE',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      if (response.status == 200) {
        alert("Deleted all work sends")
      } else {
        alert("Start database")
      }
      
}

async function getAllPosts() {
    let response = await fetch('http://localhost:8080/post/getAll', {    
        method: 'GET',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      

     await response.json().then(ar => {
        console.log(ar)
        if (response.status == 200) {
            alert("Console")
          } else {
            alert("Start database")
          }
      })


}

async function getAllUsers() {
    let response = await fetch('http://localhost:8080/fetch', {    
        method: 'GET',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      

     await response.json().then(ar => {
        console.log(ar)
        if (response.status == 200) {
            alert("Console")
          } else {
            alert("Start database")
          }
      })


}

async function getAllWorkSends() {
    let response = await fetch('http://localhost:8080/getWork', {    
        method: 'GET',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
      })
      

     await response.json().then(ar => {
        console.log(ar)
        if (response.status == 200) {
            alert("Console")
          } else {
            alert("Start database")
          }
      })


}
document.getElementById("getAllUsers").addEventListener("click", ev => {
    getAllUsers()
})

document.getElementById('getAllPosts').addEventListener('click', ev => {
    getAllPosts()
})

document.getElementById('getAllWorkSends').addEventListener("click",ev => {
    getAllWorkSends()
})



document.getElementById("delUsersButton").addEventListener('click', (ev) => {
    if (+document.getElementById("deleteElementID_input").value) {
        deleteAllUsers(+document.getElementById("deleteElementID_input").value)
    } else {
        alert("Enter id")
    }
    
})

// document.getElementById("delOtziv").addEventListener('click', (ev) => {
//     if (+document.getElementById("deleteElementID_input").value) {
//         deleteOtzivById(+document.getElementById("deleteElementID_input").value)
//     } else {
//         deleteAllOtzivs()
//     }  
// })

document.getElementById('delWorkSends').addEventListener('click', (ev) => {
    deleteAllWorkSends()
})




async function login(userLog) {
    let response = await fetch('http://localhost:8080/login', {    
        method: 'POST',
        headers: {'Content-Type': 'application/json; charset=UTF-8'},
        body: JSON.stringify(userLog)
      })

    await response.json().then(ar => {
        currentUser = ar
        localStorage.setItem("curr-user", JSON.stringify(ar))
        alert('logged')

        document.getElementById('username').textContent = currentUser.name
        document.getElementById('phoneNumber').textContent = `Номер телефона: ${currentUser.contactInfo.phone}`
        document.getElementById('profil').style.display = "flex"
        document.getElementsByClassName('bonuses')[0].style.display = "grid"
        document.getElementsByClassName('zakazi')[0].style.display = "grid"
        document.getElementById('exitAcc').style.display = "block"

        if (currentUser.admin == true) {
            document.getElementById('adminPanel').style.display = "flex"
        }
    })
}










 



    document.getElementById('buttonAuth').addEventListener('click', (ev) => {
        ev.preventDefault()

        let form = document.forms.authForm
        let name = form.name.value
        let number = form.phone.value

        let userL = {
            name: `${name}`,
            phone: `${number}`
        }

        login(userL)
    })

    

    