# The Mathematics of Fixed Income — Lecture 2
### Copyedited Transcript

---

Today I'm going to talk about fixed income mathematics, and what I'm going to be aiming for is to understand the relationship between time and money. It's all going to hinge on our ability to pick the right coordinate system. It's very similar to physics. If you try to understand the relationship between space and time, you have Newton's equations, which basically tell you that they are related to each other. And then you have Einstein's relativity, which tells you further that the concept of time is linked to the concept of space. You cannot separate the two. In finance, we have something similar. Although we think of time and interest rates from a very simplistic perspective, today is going to start a new journey where we will see that time is just part of finance. And in a certain sense, this is what was hidden in the calculation of the yield curve that we started last week.

Okay, this is a review of all of last week. There was this concept of yield. We're going to be a little bit picky with terms today. Yield to maturity is how I will refer to what, in the database on the website and in the newspapers, is called yield. I call it yield to maturity to distinguish it from the yield curve that we will use today, which in some books is called the spot curve — but we'll talk about that later.

So the usual convention is that when you have a bond, a bond has coupon payments, denoted in that expression by the letter P, that will happen at certain times, denoted by the letter T. And the price of that bond — it's the confluence of two prices: the clean price, which is quoted to you by the market, and the accrued interest on coupon payments, which is calculated based on accounting conventions. The sum of the two gives us a dirty price. Dirty because it includes fixed income and capital gains. But that captures the entire economic value of my bond in a world without taxes. That is the full value of my bond.

And we create a mental construct called R, which is the interest rate at which we would discount future cash flows to get the value today. But that's a mental construct. Financial markets do not need this R to function. We humans need it to understand what we're doing.

So the clean price is quoted and the accrued interest is calculated. Both of them give rise to the mental construct called R, which in this case is an annually compounded interest rate used to calculate the yield to maturity.

Now, talking about coordinate systems: this is the wrong coordinate system. Because if you reflect on this expression that we have here, we see that this R is a function of a bond — it's not a function of time. And I repeat: if you think that because a bond has a maturity time, this R could be a function of time because of that, the answer is no. Because the bond has a maturity time, but it also has times at which coupon payments are paid. So a bond is really a function of many different time variables, and you end up with a function which is really a function of the bond. You cannot link this R to a specific time variable.

So what we do — what we did — is we eliminated that perspective to introduce another one. Since we're doing mental constructs, we should do the mental construct which is the right one for our purposes. And our objective is to understand how interest rates are a function of time. To understand the price-time space, we need that. And for that, what we did is say: I am searching for that function, that curve — that yield curve, that spot curve — that R of T which is the same for all bonds. It's a function of time, it's a function of a single time variable, and all bonds would be priced with it. That is what I'm aiming for. If I do that, then I've built some very interesting relationship between time and money.

This is what we call the yield curve, sometimes called the spot curve, and it's the one that you have to calculate in Assignment 1. That's what we discussed last week. And I cannot stress enough that what you have on the right and on the left are different things — very different things. And different not just from a calculation perspective; philosophically they are completely different. The coordinate systems in which they live are completely different too. And that's what matters to us today.

We also saw last week that if I have that R of T, not only can I price bonds — I could even start to price stocks and other things, and that will become more clear next week. So the process will be: we focus on the dirty price — always the dirty price from now on — with instantaneous compounding, which eliminates a compounding variable and makes things easier. We aim for the curve R, which will price every bond. You can also do it with annual compounding, but then you are dealing with a choice — which compounding convention to use. If you go semiannual compounding, you start introducing another variable. I prefer to eliminate that variable by focusing on instantaneously compounded interest rates.

So, questions about this curve. First: does this curve exist? It's nice to talk about a curve that will replace everything, but does this curve exist? And if it does exist, how do we calculate it? That's your Assignment 1. Whether the curve exists or not is not addressed in Assignment 1 — it's in a theorem we will prove in a few weeks. I will actually prove one theorem in this course, and that's it. I will prove what's called the fundamental theorem of asset pricing. I will prove that all prices have to be consistent with each other, and that certain objects will exist because of that and will be unique — that yield curve is one of those objects. We'll get to that in a more general context. It's the only theorem I will prove in this course.

And then we want to know how this curve changes through time, and you're calculating that in Assignment 1. So today I will talk about Assignment 1 and what else it gives us. We will see that it's actually going to give us many things. It's going to unlock the basic relationships between time and money when you look at financial markets — not only for payments, but we're going to start to price forwards and futures today. And you will see that this curve is going to be everywhere.

So the exercise started with zero coupon bonds, which are idealized objects. They exist sometimes — for example, if you have a bond that matures in less than six months, that technically has a coupon payment, but we can think of it as an idealized zero coupon bond where we adjust the principal by including the last payment: we get half of the next coupon payment. So it's equivalent to a zero coupon bond. And by the way, you can go to a dealer and they will construct for you any zero coupon bond you want — for a fee. But in this course, for a few weeks, we're going to assume everybody works for free. It's easier to understand finance with that assumption. After Reading Week, more or less, we will go to the real world where everybody charges a fee.

So, for a few weeks — up until Reading Week — everybody works for free. So you can go to a dealer and they will construct a zero coupon bond for you because they can engineer different instruments. But the ones that you observe in your database in the market are coupon-bearing bonds. Typically, bonds have coupon payments. But zero coupon bonds are a nice idealized way of thinking about bonds. A zero coupon bond contains a single cash flow — a single payment which will happen at the time of maturity. And because of that, it's a very simple bond characterized by only three variables: the notional, which is the payment that will occur at maturity; the price of the bond; and the time to maturity.

I'll note that if your zero coupon bond is an idealized coupon-bearing bond with a single payment left, then the notional we're talking about is really the previous notional plus one half of the annual coupon rate. So we are working in mental space.

The price of the bond is the price at which people agree to exchange the bond from one person to another — to buy and sell. With these three concepts in mind, we define the yield as we did last week: we take the logarithm of the bond price divided by the notional, then divide everything by the time to maturity, to give us the yield. So in the case of zero coupon bonds, that's how you define it, and that's how you will start your bootstrapping algorithm when you do Assignment 1. Every bond that matures in less than six months can give you a yield like that.

Again, the notional is the idealized concept of $100 plus the last coupon payment you receive. So for Assignment 1, that P will be 100 plus something. And you have to take into account that you're looking for the dirty price, not the clean price, so you have to adjust for that.

So, I want you to be very aware of when you are in the real world and when you are in your mental world, and of the relationship between the two. Because you are creating a mental world which is yours — you own it. So you understand the real world in which these transactions actually happen. Then you're in command, and then mathematics will become your superpower. Only then. If you don't understand that relationship, that superpower could backfire, and you don't want that.

Okay. So I'm reviewing — this is what we did. Now this is going to lead to the topic of today, which is arbitrage-free pricing. This is how we're going to be able to price time, and this is how we're going to be able to see how this yield curve is so useful in practice.

If we had zero coupon bonds for all maturities — which we don't, and typically we don't. If you go to that website and look for zero coupon bonds, you won't find them. They really don't exist in general. They can be constructed for you, and since we're assuming that people work for free for a month and a half, you could take that approach, but they really don't exist. But the thing is: if we had them, then all coupon-bearing bonds need to be priced accordingly. You take the payments that the coupon bond will give you, you discount them with the yield curve you constructed from your zero coupon bonds, and that should be the price.

And the argument is this: if this price is cheaper, then everybody would be selling the other bonds and buying these ones. And if this price is more expensive, then everybody will be selling these and buying the other ones. That's how price formation happens. Now, in this course we're not looking into price formation — that is what economists do in other courses. We're not going to do that here. Here, we assume that we always observe prices once equilibrium has been achieved. Sometimes it takes months for equilibrium to be achieved. In the theory we're dealing with here, we assume that equilibrium has been achieved.

This is a very important observation, because I'm going to say here that there is no arbitrage in the markets. And in fact there are people who make their living through arbitrage. What happens to your jobs? Well, they exist because arbitrageurs are the ones who drive markets into equilibrium, and they get paid for that. But since we're assuming no one is getting paid to do anything for a month and a half, these people don't exist for us. Or rather, they exist, but we show up after they've made their money and after the market is at equilibrium. Do you understand what I'm saying?

This is a very important topic because, if you go to the financial industry, you will find a lot of criticism of the arbitrage-free or efficient market hypothesis. The criticism is usually from people who don't understand why we make those assumptions. You've studied physics and you always assume that things are idealized — air has no weight, or sometimes it has this weight — and you make your assumptions to solve a certain problem. But you're always aware that you're solving that problem under idealized conditions of temperature and pressure, and so on, and then you proceed to the real problem. We always work like that. Finance is no exception. We start with the simplest situation — prices have been formed — and then we understand what's going on.

This will be like that until mid-February. After Reading Week, everybody is going to be making money. Until then, we all work for free. Okay?

If someone can make money for free, we call that an arbitrage. An arbitrage opportunity. For a month and a half, we're going to assume those don't exist.

So, if this curve exists, it has to be unique. At least we know that much. Why does it exist? The existence of this curve, as we will see, is linked to the existence of prices in financial markets. I'll leave that for another couple of weeks.

Now, bootstrapping is your Assignment 1. It's the name we gave to this process where you calculate the yield curve. Starting with the very short maturities — where bonds have a single payment, and therefore the yield can be calculated directly — and then you go, in the next stage, to bonds that have two payments. Because for the two-payment bond, what we have is: the first payment is discounted with a yield that we already know. I remind you: this yield is good for every bond. Footnote: not only will it be good for every bond, it will be good for every bond, every stock, every futures transaction, every option — it prices everything. So in particular, it prices every bond.

That means that when I look at the dirty price of my bond — which is known — and I see the first term, that first term is something I can calculate using the yield from a different bond, from a zero coupon bond. This leads to my ability to calculate the only unknown in that expression, which is r of T₂. That's the key. That's why bootstrapping works. I can see some of you nodding. I need to make sure that everybody understands this, because this is critical. In this equation, there's only one unknown.

> **Student:** So we use one rate for six months and then another for the second period. Is it assumed that we buy it at the half-month mark, or buy it now?

No. This has a published price — because it has a published price, someone bought it. Not you — someone else. You're just an observer, and you're building a mental picture of the market that's happening in front of you. You don't have to buy or sell anything. Okay? So you observe that someone bought it. And you ask: given that someone bought it, what is the yield implied by that price? That's how you do it.

So what you're doing — and this is very interesting — is that we are taking the database given to you, which is bonds and prices, and we're changing that database into a curve that captures all the parameters in the entire database of all bonds traded today with a single curve. That's the power of this. And this curve, as we saw, has exactly the same information as all those bonds, because you can price every bond from it. We're just changing the coordinate system from one that looks very messy and complicated — with bonds and prices and coupon payments and so on — into one which is very clean: the curve.

This is a tremendous exercise — not in data compression, but in understanding why all those prices are the way they are. And then you can extend to bonds with maturities from one year to a year and a half, a year and a half to two years, two years to two and a half years, and so on and so forth. That's why it's called bootstrapping. And that's your Assignment 1.

And when you finish Assignment 1, you will be very powerful — guaranteed. Because not only will you have learned how to do that, but you will also have learned that when you make a mistake — and you will make mistakes: we're going to make approximations, this and that — eventually, you're going to have to divide by T₂ to calculate R₂. If that T₂ is very small and you divide by it, whatever error you made is going to be amplified. And the fact that you do it with your own hands — of course, with Python or whatever — but the fact that you're actually calculating that and feeding it real data is what allows you to understand that these data elements that go into your algorithm come from the market. You're making assumptions. You're making approximations. And you've learned that when you make approximations, those errors could blow up in your face if you're not dealing with them in the right way. Okay. And that's why we asked for that in the assignment.

Okay, great. So that's Assignment 1. But now I want to look at the time dynamics of that, because you're doing Assignment 1 not for just one day. That would have been nice — and in fact, doing that assignment for just one day puts you ahead of 90% of the students who take courses like this around the world. But now I want you to go into the curve dynamics. And when we look into the curve dynamics, some very interesting things happen. And that's where the mathematics is going to become very, very powerful. It's where that coordinate system that expresses prices with curves becomes extremely powerful. It really is a superpower.

So for that, I need to introduce a new time variable, and I need to be very precise when I talk about time. There are going to be two time variables: lowercase t and uppercase T. Lowercase t is the time of day — it's the time on my watch — and I call it time. Then there's uppercase T, which is the time to maturity. That is in the database; it's not on my watch. And I call it term, or sometimes tenor. Okay: lowercase t, uppercase T.

We're just being aware of these two time variables. The yield is the same as before, because when we said "time to maturity," that's the time of maturity minus the time today. In all of our calculations earlier, I was assuming lowercase t equals zero. My clock says zero. So then T is the time to maturity. But now, because time will be moving from one day to the next — or from one second to the next — I have two time variables to deal with. I haven't changed anything. It's the same thing as before. And I can define the yield for zero coupon bonds exactly the same way, but now I keep track explicitly of both time variables: time and tenor.

And it tells me that the yield rate will be the negative logarithm of the price of that zero coupon bond P(t, T), divided by the time to maturity T minus t.

As a function of T, r is smooth. When we develop models, it will be a smooth curve — it's continuous, it has derivatives, it's a nice curve we can work with. But as a function of t, it's going to be continuous but will almost surely never have derivatives. Rates go up and down, up and down, up and down — very similar to the way stocks move. In fact, this is the first time we see an object that we will model in a few weeks when we study random walks and stochastic calculus.

The behavior as a function of the two time variables is very different. As a function of T, it's very nice. Of course, when you do the calculation in your assignment, you're going to get kinks, because you're going to do linear interpolation. But again, you need to be very well aware that that's just a function of the model you chose to build. If you had infinitely many bonds for all possible maturities, it would be smooth. But then as you check different prices every day, you will see that rates go up, rates go down. So the time variable will introduce that lack of differentiability.

> **Student:** Sorry. So for the R in the left equation — is R a function on its own, not like... and T minus t is not the parameter in the function, right? So it's R multiplied by T minus lowercase t?

R is a function of two variables, right? So it's r(t, T) times (T − t). That's how I defined it. Yes. Because I was just wondering where the T minus t came from in the right-hand expression.

Okay. So, if I had been 100% rigorous — which I try to avoid, by the way, because then the notes become very confusing — that should be e to the minus r(t, T) times (T − t). That's where it would be exactly right. So the R that I have there — I did not mean in any way that it's a constant. It just happens to be a function, and I give you the function on the right-hand side. Yeah, I do that because I think it's easier to understand; I also understand it could be misleading. So thank you for pointing that out.

Right here, it seems that R was meant to be constant, or maybe a function of capital T only. But no — I did not imply R to be constant. That's why I wrote it on the right-hand side as a function of the two time variables. Now it's clear.

Okay, good. Now, properties of yield. It has two time variables: time of day and term. And then the bond price is a function of both. We're going to assume that the price of zero coupon bonds is between zero and one — with notional one, which is the convention mathematicians like because it eliminates another variable. When I say that the bond price is between zero and one, that's equivalent to saying, for example, that interest rates are non-negative. Negative interest rates would make the price of a bond possibly lower than zero, or possibly greater than one.

Do you know if interest rates ever become negative? Yes, they do. It's rare, but there was a period around 2009 and 2010 where we had negative interest rates for over a year. Going back to my earlier explanation: the theories we're going to discuss here apply after price formation has happened. So those things we will just consider aberrations, and we wait to develop these theories after those aberrations have vanished.

And when I say that the value of my bond at T equals t is one — P(t, t) = 1 — that means that if I take a dollar from you and I sell it back to you immediately, it's a dollar. That's a reflection of the fact that I'm saying there are no transaction costs, which is the same as saying people work for free. Okay. So these are some of the things we're going to be developing in this course.

Now, the first secondary mathematical object I'm going to create today is the concept of the instantaneous cost of borrowing. The instantaneous cost of borrowing is: what interest rate do I pay you if I take some money from you and give it back to you right away?

Before I talk about that, let me tell you this is a very important concept — not because people do it all the time, borrowing money to give it back immediately, but because there's a very big market for overnight lending. The banking system is a very large system where everybody does transactions with each other. So often, instead of bank A settling all its transactions with bank B immediately, bank A says, "How about if I just don't settle? I just owe you." And bank B says, "Sure — how much?" So they carry it overnight. Overnight means between now and when we open tomorrow, so it's considered to be essentially instantaneous.

This is actually a huge market. It's the market that gave rise to the term some of you may have heard of: LIBOR — the London Interbank Offered Rate. That's exactly what it is: the interest rate that banks would charge each other for these overnight transactions at the end of the business day. And this LIBOR rate was so important that, once upon a time, some banks conspired to manipulate it. Big fines, big investigations. Why? Because the LIBOR rate is published every day and has become a reference that many other transactions use — whenever they have to settle trades with each other, they settle at LIBOR. So if you manipulate it, you're manipulating a huge market. That's fraud, and it happened.

From our perspective, we're in the business today of creating mental objects to understand financial reality. From that perspective, what is the instantaneous cost of borrowing? It's the limit when term T goes to time t. It's a limit. If you go to my equation, if T equals t, I'm dividing by zero — can't do that. So it has to be a limit.

If I take the limit when T goes to t — and note that T is always greater than t, so the limit is from the right — what do I get? That's a derivative, isn't it? Well, some of you may say: no, it's not a derivative, I'm missing something in the numerator. You're missing the number zero, but the number zero is log of P(t, t). We just discussed that P(t, t) equals one, so log of P(t, t) is zero. Add that on top and then you see that the limit when T goes to t is a partial derivative. Specifically, it's −∂/∂T log P(t, T), evaluated at T = t.

This is the short rate:

$$r_t = r(t,t) = -\frac{\partial}{\partial T} \log P(t,T)\bigg|_{T=t}$$

So LIBOR is essentially the partial derivative of our yield curve. This is very interesting because it shows that our yield curve is actually useful for calculating other things, like LIBOR.

Alright. Now let me move on, because I'm not going to stop at LIBOR. I want to get many other things out of that curve today. For that, I want to move forward in our view of financial markets by talking about forwards and futures.

A forward transaction is a transaction where I agree to do something with you, but we'll do it later — not now — though we agree on the price today. That's a forward transaction. Essentially, when you buy something from Amazon it's like that: you agree on the price, and it's shipped to you. They typically charge you when it arrives. If they charge you earlier, that's not a forward; if they charge you when it arrives, then it's a forward transaction. And you do these transactions all the time.

Now, a futures transaction is similar, except that in a forward you have a counterparty that is responsible for the delivery, whereas in a futures transaction you have an exchange that's responsible for the delivery. The difference is huge because an exchange will always honor its obligations, whereas a counterparty may go bankrupt. But for the next month and a half, people work for free and everybody does what they're supposed to do. So no bankruptcies. For us these two are the same, but you should know that in reality they are very different. And I remind you that the rice exchange in Osaka at the end of the 17th century was a futures market — the first futures market where a central market institution was responsible for the delivery mechanism and enforced payments. No credit risk, no default possibilities.

Okay, we talked about that last week. So now we're in a position to start using our curve to price futures. For that, I'm going to do the following exercise.

You have Apple stock. What's the value of Apple stock today? [Someone says 261.] 261. Okay. We declare Apple stock to be $261.

Imagine you want to buy Apple stock, but not now — you want to buy Apple stock a year from now from me, and I'm going to sell it to you. At what price shall I sell you Apple stock a year from now?

Let me ask another question first — a completely different question. What will the value of Apple stock be a year from now? No one knows. Okay? No one knows. If I could answer that question in this course, this course would be at Hogwarts. Not U of T. Okay?

But I can answer the question: at what price will I sell you Apple stock in a year? That I can answer. And it's a different question, as you're about to find out.

We call that APPL(0, 1) — in agreement with the notation we're developing today, where 0 means I agree now and 1 is when I deliver in a year.

Now, for that, I'm going to introduce something that will be our companion for the next month: the concept of a replicating portfolio.

If Apple stock is $261, what I do is simply borrow money. I borrow $261 from you. Good. Then I buy Apple stock now. In a year, I sell it to you at price X, and then I pay you back. But I know how much I owe you, because we agree on the interest rate. So if we agree on the interest rate, I know exactly how much I'll have to pay you back at maturity. And that tells me exactly how much I have to charge you.

You see that? So this is the forward — or futures — price of Apple stock. Forwards and futures today are the same because there's no default risk and everybody works for free.

I have not determined the price of Apple stock in a year. I don't know how to do that. But I can determine the price at which I will sell you Apple stock in a year such that we all break even. Therefore:

$$\text{APPL}(0,1) = \$261 \cdot e^{r(1)}$$

> **Student:** I guess because if you buy the stock now rather than using the money to do something else...

Exactly. Yes. I look — I never claimed I was going to do something very complicated, like building a trading machine that buys and sells depending on price movements. This does it for me. We're going to do a lot of replicating portfolios.

This is called a replicating portfolio. And then we have that the value of Apple stock is — in fact, you can generalize this expression to any stock at any time t, for any term capital T:

$$S(t,T) = S_t \cdot e^{r(t,T)\cdot(T-t)}$$

and the yield curve does it for us. So the yield curve prices forwards and futures.

> **Student:** It seems you can do it with anything.

With almost anything, yes — but this is just the first step in climbing to a new mountain, to gain a new perspective. So what I want to do now is do it for bonds.

For bonds, it's going to be a bit more complicated. Let's say that you want to buy from me a two-year bond a year from now. Can you do that? The bond doesn't exist yet, because it will be issued in a year but not now. So the same trick I did for Apple stock doesn't work, because I'm trading something that doesn't exist.

You might think: can I think of it as buying something with a certain term? Yes — I will teach you how to think about these things so that you don't get stressed. It's very easy. You just need to collect and organize your information in the right way. This course is going to be easy most of the time. But now we need an idea we haven't needed yet. This might look like magic, but it's not Hogwarts — it's still U of T.

So for that, what I need to do is something a bit more sophisticated — but it's also a replicating portfolio. Just pay attention.

I'm going to set up the following contract. The contract has:

- **Agreement date:** now (time t)
- **Product to deliver:** a zero coupon bond B issued at T₁, paying $1 at T₂ — which doesn't exist yet
- **Delivery date:** T₁
- **Price:** unknown — P(t, T₁, T₂)
- **Payment date:** T₁

So let me summarize everything I just said in a table. There are only three dates at which payments happen.

| Date      | Today | T₁              | T₂ |
|-----------|-------|-----------------|-----|
| Cash flow | 0     | −P(t, T₁, T₂)  | 1   |

Today: cash flow is zero — we just agree, nothing is exchanged. At time T₁: that's when I sell you the bond and you pay me P(t, T₁, T₂). At time T₂: you receive $1.

In the case of Apple stock, we only had two dates; now we have three. But is anyone scared of the number three? If you can do two, you can do three. You can do four. You can do infinitely many — you just need to organize everything correctly.

For that, I'll build a portfolio consisting of two zero coupon bonds. One bond will mature at time T₁, and the other at time T₂. I will come up with a portfolio of these bonds with unknown quantities. In the Apple stock case, I knew I had to buy one stock and borrow some money. Here I need to figure out what to do.

I'm going to select the number of bonds at T₁ and T₂ so that the cash flows match.

Let's start matching the cash flow at time T₂, since that's the easiest: you're going to receive $1. That means the bond maturing at T₂ has to pay $1. Assuming zero coupon bonds have notional $1, my portfolio will hold one bond maturing at T₂.

Now, how many bonds maturing at T₁ do I need? Let's look at the cash flow matching challenge today. I know what the value of my T₂ bond is: it's P(t, T₂). And I know the value of the bond maturing at T₁ is P(t, T₁). If I want the total cash flow today to be zero — matching the zero in my forward contract — how many T₁ bonds do I need?

The answer is:

$$x = \frac{P(t,T_2)}{P(t,T_1)}$$

bonds sold short. So the replicating portfolio consists of 1 long bond at T₂ and −x bonds at T₁.

Let me ask you: how much money do I have to borrow from the bank to do this transaction? Zero. Because I need to buy the T₂ bond at cost P(t, T₂), but I'm going to sell x units of the T₁ bond, which raises x × P(t, T₁) = P(t, T₂). So the total cost is zero. This is a transaction I can do for free — I don't even have to go to the bank. It's grade-four multiplication with big variables.

So the value of this replicating portfolio is zero. It has zero cash flow today — matching my forward contract. And it delivers $1 at T₂ — matching my forward contract. Therefore, the cash flow at T₁ must also match. That means the price I will charge you at T₁ is:

$$P(t,T_1,T_2) = \frac{P(t,T_2)}{P(t,T_1)}$$

If you pay me more, I make money for free. Not allowed. If you pay me less, you make money for free. Not allowed. It has to be exactly that.

> **Student:** Why is it positive? Not negative?

Ah — it's negative. It has to be negative. There's a minus sign there that ended up in the wrong place — it's a typesetting error. Let me be clear: in the cash flow table, the entry at T₁ is −P(t, T₁, T₂), because you pay me. So that's negative. Just agree with yourself on sign conventions, and make sure things are internally consistent.

Is this clear now? I want everybody to understand it — it's very easy, but everything changes once you've climbed this hill. With this, we can start to do so much more.

So from there — and that's because we're mathematicians, so we have a license to define — I'm going to define a new yield. It's called the forward yield. And I define it analogously to the definition of the bond yield. It's just a definition. There's nothing to explain — it's there. But see, it looks plausible. It looks like it could be useful. It's somewhat useful. But the one that is very, very useful is the forward rate — specifically, the instantaneous forward rate, also called simply the forward rate. The forward rate is the instantaneous forward cost of borrowing, which is the limit when T₂ goes to T₁. Again, this is another partial derivative. Just look — you've seen derivatives; that's it.

So the forward rate is the partial derivative of the logarithm of the bond price with respect to term:

$$f(t,T) = r(t,T,T) = -\frac{\partial}{\partial T} \log P(t,T)$$

This is very important. There are three things that matter here. First: that's a differential equation that I can invert. I can solve it. I can go from forward rates to bond prices. By inverting it — integrating both sides — the bond price is:

$$P(t,T) = \exp\!\left(-\int_t^T f(t,u)\,du\right)$$

That's the simplest differential equation you've ever seen, and it's solved by integration. So a forward rate contains exactly the same information as the yield curve, because I can price every bond. I can go from bond prices to forward rates, or from forward rates to bond prices, without losing any information. That's very important.

And by the way, that implies that if I look at the fixed income market today, I know what the forward rates are. I know how much I should pay for a bond that will be issued in the future.

Let me talk about the finance of that — no math, just the finance. Who would be interested in buying Apple stock a year from now? Maybe you think Apple isn't doing so well. Okay. So you would use a forward for speculation purposes — especially if the forward price seems cheap or expensive relative to your expectations.

You can do the same for bond prices. You can speculate about interest rates. But there's another reason I want you to understand, because the forward bond market is very big. Do you know what a pension plan is? Canada Pension Plan. Most of you have money with the Canada Pension Plan. If you've ever been employed in Canada, some amount — a few hundred dollars — went into CPP. So some fraction of the 700 billion dollars they manage is yours.

They have armies of people doing bond trading, because that's what CPP does: they take the money that comes in from all of us and ensure it stays valuable and grows with inflation. And how do you do that? By going into the bond market.

The thing is: CPP knows very accurately how much money is coming to them every month. Because the contributions are more or less constant — my CPP contributions are almost the same every month. So they know a billion dollars is coming next month. And they have to go buy a billion dollars' worth of bonds. But if every pension plan in Canada shows up on the same day to buy bonds, what happens? You're going to overpay. So they use forward contracts to lock in prices ahead of time, avoiding a crowded and expensive trade. That's one important use of forward bond contracts.

So always think about the finance behind the math we're doing.

---

## Yield Curve Dynamics

So now I move to the next topic. And something I mentioned last week is now becoming more real, because Assignment 1 is addressing it. I showed you a mockup of what your yield curves might look like. You won't have three — you'll have ten — but they'll look something like this. By the way, has anyone already done the yield curve calculation? Got something like that? Okay.

What I want to tell you is about the dynamics of this curve and the mathematics that goes into that. The movement is going to be — as I mentioned — a superposition of three main directions.

**1. Parallel shift:** The most important direction — all rates go up or down together by the same amount. You may have seen this: for example, you probably saw that employment numbers in Canada were kind of weak recently. That means there's pressure to lower rates. So maybe in the yield curve you're calculating, you see it going down overall.

**2. Curve steepening (tilting):** Why? Because money has different values today versus a year from now.

**3. Convexity:** What happens to the medium term relative to the two ends of the curve.

These three components drive the markets, and they're built into the variance-covariance matrix you're calculating in Assignment 1.

---

## Principal Components and the Music Analogy

But before you do that, let me show you a variance-covariance calculation that is easier to understand first: what happens when I look at stocks.

I haven't done stocks yet. We're still trying to understand the value of time. But by comparison — and because it'll be easier to understand — let me tell you what would happen if I take a universe of stocks. Say 10 stocks, or 60 like the S&P/TSX 60 index, or 500 like the S&P 500. Take a universe of at least two stocks, hopefully more. If I take 10 stocks and I look at the daily percentage changes — as I asked you to do in Assignment 1 — and you calculate the variance-covariance matrix of those changes, you're going to get a certain variance-covariance matrix.

This is the spectral decomposition. Variance-covariance matrices are typically easier to understand from the spectral perspective. And I assume everybody knows what eigenvalues and eigenvectors are. Anyone who doesn't, please raise your hand — not to be kicked out, but because I need to know so I can explain it quickly. Everybody knows. Good.

So if I take the eigenvectors and eigenvalues of the variance-covariance matrix of a universe of stocks, what I get is what you see in the slides. The most important part is the percentage of explained variance: the percentage that each eigenvalue represents relative to the total trace. The trace is the sum of all eigenvalues, which equals the sum of the diagonal elements of your matrix.

So what we see is: the highest eigenvalue has a corresponding eigenvector. Now, what's the eigenvector for the highest eigenvalue? Can someone read it to me?

> **Student:** Like a bunch of random negative numbers.

Thank you for that answer. They're not random. And second: they're not all negative. Remember that an eigenvector is determined only up to a multiplicative constant. You can multiply it by any number — including minus one — and it's still an eigenvector. So the fact that you see negative numbers is because when you ask the computer for the eigenvector, it follows an algorithm and doesn't know that an eigenvector lives in projective space. You can multiply it by any scalar you want.

So maybe I need to remind you what an eigenvector is. When you have a matrix and you think of it as a linear transformation of Euclidean space, an eigenvector is a direction which is left invariant by the matrix. It's a direction — not a vector. It could be this direction or the opposite direction. Any vector along that line represents the same direction. So when you see −0.3-something for all ten entries, you can multiply by a negative constant, and then you see that all entries are more or less the same size. That's why I'm saying: the eigenvector you should see there is essentially (1, 1, 1, ..., 1).

> **Student:** So the curves move in the same direction?

No — I'm not talking about the yield curve right now, I'm talking about stocks. Let me explain eigenvectors more carefully.

An eigenvector is a direction kept invariant by the matrix. And something that's invariant is important — guaranteed. This is an engineering mindset: if something doesn't change, pay attention to it. A bridge that's been standing for 500 years — study it. A government that hasn't changed for a thousand years — look into it. Invariant things encode important information.

Now: eigenvalues give us the size of the components of volatility in each direction, and eigenvectors give us those directions. The source is the eigenvector; the size is the eigenvalue.

So when I look at this: it's telling me that 55.7% of the movement of stocks in this universe is determined by that first portfolio — the one where all stocks have roughly equal weight. And since all the entries are more or less the same, that portfolio is essentially the index. If you're long, and I tell you the index went up today, you're happy — because you made money. Why? Because the index is precisely defined by the first eigenvector — the one that maximizes the correlation with everything else. So if you have to pick something that maximizes the information you give to all stock investors in the world, it's the index as defined by the first eigenvector of the variance-covariance matrix. Now you understand eigenvalues and eigenvectors. That's what they are.

---

## Fixed Income Factors

In your Assignment 1, I'm asking you to:

1. Compute all yields r_{t,T} for each day t and each tenor T.
2. Compute percentage daily changes: (r_{t,T} − r_{t−1,T}) / r_{t−1,T}.
3. Compute the variance-covariance matrix of those changes.
4. Compute eigenvalues λ₁ ≥ λ₂ ≥ λ₃ ≥ ... and the corresponding eigenvectors v₁, v₂, v₃, ...

What are those eigenvectors? I predicted them at the end of last week's class. And now I'm going to tell you again:

- **v₁ ∼ (1, 1, 1, ..., 1):** The parallel shift. The most important direction in fixed income markets. It killed **Silicon Valley Bank**. Eigenvectors can kill.

- **v₂ ∼ (1, 1, 1, ..., −1, −1, −1):** The curve steepening factor. This is the eigenvector that killed **Orange County** in 1994 — the biggest municipal bankruptcy to that date. Bob Citron, the treasurer, was duration-neutral (no exposure to v₁) but had enormous exposure to v₂. When the Fed raised rates sharply at the long end, his repo contracts lost money very fast. Twenty percent of explained variance is not trivial: if you're a bond trader with exposure to a direction that explains 20% of movements, that can destroy you.

- **v₃ ∼ (1, 1, ..., −2, −2, ..., 1, 1):** The convexity factor. It's harder to find casualty stories, but it's the eigenvector associated with the **Beacon Hill** hedge fund in 2002. After quantitative easing was initiated by Alan Greenspan, it cheapened the belly of the curve and created large-scale mortgage prepayments across North America. Beacon Hill had exposure to the belly of the curve, and when that went down, they blew up.

Eigenvalues and eigenvectors can kill in the fixed income market. The eigenvectors tell you which directions to watch, and the eigenvalues tell you how intensely to watch them. Your Assignment 1 will give you a spectral picture of the fixed income market.

Have you heard the term "spectral" before? What does it come from? The Greek for "light." It was first understood by astrophysicists, who saw that light from distant stars appeared only at certain discrete frequencies, with nothing in between. Now we know why — from quantum mechanics. The word "spectral" comes from the picture of light.

Here is an interesting comparison: the variance-covariance matrix for a group of stocks versus the same for a group of hedge funds.

For **stocks**: the highest eigenvector is very dominant and the relevance drops quickly. It's a very ordered system — like **music**. There's a strong fundamental, with overtones dropping off rapidly.

For **hedge funds**: hedge funds go long and short, and by going short you already destroy much of the dominance of the first eigenvector — because you're partly hedged. So the eigenvalues are flatter, more evenly spread. Much harder to understand. I like to call this **noise**, as opposed to music in the stock market. Not that noise is bad — it's just hard to understand.

---

## Pythagoras, Music, and MP3

Now, let me tell you how this was invented, and I have to go back to Pythagoras.

Pythagoras was a very interesting figure. He used to walk to his school, and on his walk there, he had to pass a forge where they make metal rods. They were making several metal rods simultaneously, hammering them. And he became curious because some days the sounds made by those rods being struck were very pleasing to the ear, and other times they were not. Talking about 2500 years ago.

What he discovered is this: if you hit two metal rods of lengths P and Q, and the ratio P:Q can be expressed as a fraction with small integers, they sound good together. If they require very large integers in the ratio, they sound bad together.

He also proved that the square root of 2 is irrational, and conjectured that two rods in that frequency ratio would sound unpleasant — and they do. That interval is called the tritone. Meanwhile, small integer ratios — like 4:5 (a major third) — sound consonant and pleasant. This is built into our DNA; it's universal across cultures and languages.

Fast forward to today. Pythagoras's theorem extends to infinite dimensions — that's the Parseval identity, the foundation of Fourier series. And from that, we get MP3.

Every sound is a combination of cosine waves at different frequencies. If you tell me what combination of frequencies you need to reconstruct a given sound, I can throw the sound away and just give you a list of numbers — how much of each frequency to use. That's what you download. Your smartphone stores those numbers in memory, and when you want to play music, the decoder takes those numbers, plays those frequency components, adds them together, and you get the original music back. That's encoding and decoding.

But what's critical is that you use the **right basis**. The basis that works for one-dimensional instruments — flute, piano, guitar, violin — is the sine/cosine basis, because those instruments are all governed by the wave operator:

$$-\partial_x^2 \,\sin(n \cdot x) = n^2 \sin(n \cdot x)$$

The sine function is an eigenvector of the wave operator, and n² is the eigenvalue. The reason MP3 works is that the encoding and decoding is done with the eigenvectors of the wave operator.

That's also why MP3 compresses concert noise badly — the crowd cheering sounds terrible in a recording, because the encoder was built for strings, for one-dimensional instruments, not for noise. And for JPEGs, you replace sine waves with wavelets or DCT basis functions — the same encoder-decoder principle, but with a different eigenbasis suited to two-dimensional images.

**What you're doing in Assignment 1 is developing the coordinate system to understand bonds.** Like the MP3 developers chose the right basis for music, you're choosing the right basis — the yield curve and its principal components — for fixed income.

What's the bit rate? A bit rate of 3 is very good in the bond market. Meaning the three largest eigenvalues will describe the motion of fixed income markets very well. In terms of portfolio management: you cannot pay attention to every possible direction that the market could move. You have to focus on the important ones. If you're going to make a bet, make it on something meaningful, not something noisy and hard to predict. That's the significance of the bit rate for portfolio management.

---

## Regression Trees and Nonlinear Encoding

The linear encoding of financial markets — using eigenvalues and eigenvectors, or principal components — has been done very successfully for decades. But now, with machine learning, we can do nonlinear encoding as well.

Imagine a database of company size and volatility. If you try to do linear regression of that relationship, it won't work well. What will you do?

> **Student:** Classification problem.

Exactly. So I'm going to build a regression tree.

These data descriptors — volatility, company size, number of employees, stock price, etc. — are called **features**. And I'm going to show you how regression trees work, as opposed to spectral regression.

A regression tree is built as follows. I decompose my feature space in a nonlinear way so that my data is broken up into rectangles that are more or less homogeneous. The error I use is the residual sum of squares (RSS):

$$\text{RSS} = \sum_{j=1}^{J} \sum_{i \in R_j} |x_i - \hat{x}_{R_j}|^2$$

where $\hat{x}_{R_j}$ is the mean of the training observations in rectangle $R_j$. I want each rectangle to be very homogeneous — the distances between elements and the center are small — which makes the RSS small. There's an algorithm to do that.

This algorithm is called **recursive splitting**. For each feature j and each split value s, I consider the pair of half-spaces:

$$R_1(j,s) = \{X \mid X_j < s\}, \quad R_2(j,s) = \{X \mid X_j \geq s\}$$

and I select $(j, s)$ to minimize:

$$\sum_{i:\, x_i \in R_1(j,s)} |x_i - \hat{x}_{R_1}|^2 + \sum_{i:\, x_i \in R_2(j,s)} |x_i - \hat{x}_{R_2}|^2$$

I do this brute-force for every possible feature and every possible split value. Then I look at what's left in each region and find the next optimal split, and so on — just like a tree growing branches.

If I'm looking for a bit rate of three, three rectangles describing what's happening might be enough. You give me a company size, I tell you the volatility. That's it, in a nonlinear way. Bit rate three.

> **Student:** Oh, this is too good. Why not bit rate ten?

Because if you have ten data points and you use bit rate ten, you're going to do what's called **overfitting**. You explain your training data perfectly — but now let me give you testing data and see how well you do. Typically, anything that overfits fails miserably on the testing data.

So how do you find the balance? Through **tree pruning**. Think of the recursive split process as a tree. Overfitting is a tree with too many branches. The way to address this is to introduce a cost function: every time you want a new branch, you pay for it. You look for:

$$\min_{T \subseteq T_0} \left[ \sum_{m=1}^{|T|} \sum_{x_i \in R_m} |x_i - \hat{x}_{R_m}|^2 + \alpha \cdot |T| \right]$$

where $|T|$ is the number of terminal nodes and α is the cost per branch.

- If α is very small → cheap to build big trees → likely to overfit.
- If α is very large → small, parsimonious trees → likely to underfit.

You need to find the optimal α through **cross-validation**. You divide your training data into folds. For each fold, you designate it as the validation set and train on the rest, then evaluate how well you predict the validation fold. You do this for all possible fold choices and all possible α values. This lets you find the optimal α. You still hold out a true testing set for final evaluation.

---

## Classification Trees

Classification trees are like regression trees, except there is no RSS — the outcome of the classification criterion is binary: "YES/NO", "TRUE/FALSE", or "1/0". Instead of the RSS, we consider three objective functions:

- **Error rate:** $E = 1 - \max_k(\hat{p}_{m,k})$ — not sensitive for tree-growing.
- **Gini index:** $G = \sum_{k=1}^{K} \hat{p}_{m,k}(1 - \hat{p}_{m,k})$ — a measure of node purity variance.
- **Entropy:** $D = -\sum_{k=1}^{K} \hat{p}_{m,k} \log \hat{p}_{m,k}$

---

## Closing Remarks

The linear systems for markets today work very well — markets are still pretty linear overall. But there are features that need to be understood with nonlinear methods like regression trees. This is still work in progress even in professional financial sectors. Very few companies are using these methods to understand financial markets. I'm pretty sure many of you will be bringing this knowledge into your workplace.

But be careful: some employers will expect magic. And now I have to tell you something I tell all my math students: **math is your superpower** — not so much because you can calculate anything, but because math will tell you the limits of what can be calculated. Math is the ultimate nonsense detector. Math cannot tell you what the price of Apple will be a year from now. I know at what price I will sell you that stock a year from now. But I cannot tell you what the price will be. This ability to know what you can and cannot do — that is going to be one of your superpowers.

I encourage you to watch Leslie Lamport's talk on the difference between programming and coding — it's a good inspirational video and very relevant to how we think about mathematical structure versus implementation.

Thank you.

---

*Key corrections made: fixed recurring terminology errors ("acred" → "accrued," "couponary" → "coupon-bearing," "stastic" → "stochastic," "labore"/"labor"/"libore" → "LIBOR," etc.); removed false starts, filler repetitions, and mid-sentence restarts; standardised capitalisation of mathematical terms (T₁, T₂, etc.); corrected proper nouns ("Bob Kitong" → "Bob Citron," "Leslie Lampbert" → "Leslie Lamport," "Pacin Hill" → "Beacon Hill"); preserved all substantive content and classroom exchanges.*
